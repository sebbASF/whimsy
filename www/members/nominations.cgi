#!/usr/bin/ruby1.9.1
$LOAD_PATH.unshift File.realpath(File.expand_path('../../../lib', __FILE__))

require 'mail'
require 'wunderbar'
require 'whimsy/asf'

# link to members private-arch
MBOX = 'https://mail-search.apache.org/members/private-arch/members/'

# link to roster page
ROSTER = 'https://whimsy.apache.org/roster/committer'

# get a list of current members messages
year = Time.new.year.to_s
archive = Dir["/srv/mail/members/#{year}*/*"]

# select messages that have a subject line starting with [MEMBER NOMINATION]
emails = []
archive.each do |email|
  next if email.end_with? '/index'
  message = IO.read(email, mode: 'rb')
  next unless message[/^Date: .*/].to_s.include? year
  subject = message[/^Subject: .*/]
  next unless subject.upcase.include? "MEMBER NOMINATION"
  mail = Mail.new(message)
  next if mail.subject.downcase == 'member nomination process'
  emails << mail if mail.subject =~ /^\[?MEMBER NOMINATION]?/i
end

# parse nominations for names and ids
MEETINGS = ASF::SVN['private/foundation/Meetings']
meeting = Dir["#{MEETINGS}/2*"].sort.last
nominations = IO.read("#{meeting}/nominated-members.txt").
  scan(/^-+--\s+(.*?)\n/).flatten

nominations.shift if nominations.first == '<empty line>'
nominations.pop if nominations.last.empty?

nominations.map! do |line| 
  {name: line.gsub(/<.*|\(\w+@.*/, '').strip, id: line[/([.\w]+)@/, 1]}
end

# location of svn repository
svnurl = `cd #{meeting}; svn info`[/URL: (.*)/, 1]

# produce HTML output of reports, highlighting ones that have not (yet)
# been posted
_html do
  _title 'Member nominations cross-check'

  _style %{
    .missing {background-color: yellow}
    .flexbox {display: flex; flex-flow: row wrap}
    .flexitem {flex-grow: 1}
    .flexitem:first-child {order: 2}
    .flexitem:last-child {order: 1}
  }

  # common banner
  _a href: 'https://whimsy.apache.org/' do
    _img title: "ASF Logo", alt: "ASF Logo",
      src: "https://www.apache.org/img/asf_logo.png"
  end

  _div.flexbox do
    _div.flexitem do
      _h1_! do
        _ "Nominations in "
        _a 'svn', href: File.join(svnurl, 'nominated-members.txt')
      end

      _ul nominations.sort_by {|person| person[:name]} do |person|
        _li! do
          match = /\b#{person[:name]}\b/i
          if emails.any? {|mail| mail.subject.downcase =~ match}
            _a.present person[:name], href: "#{ROSTER}/#{person[:id]}"
          else
            _a.missing person[:name], href: "#{ROSTER}/#{person[:id]}"
          end
        end
      end
    end

    nominations.map! {|person| person[:name].downcase}

    _div.flexitem do
      _h1_.posted! do
        _a "Posted", href:
          'https://mail-search.apache.org/members/private-arch/members/'
        _ " nominations reports"
      end

      # attempt to sort reports by PMC name
      emails.sort_by! do |mail| 
        mail.subject.downcase.gsub('- ', '')
      end

      # output an unordered list of subjects linked to the message archive
      _ul emails do |mail|
        _li do
          href = MBOX + mail.date.strftime('%Y%m') + '.mbox/' + 
            URI.escape('<' + mail.message_id + '>')

          if nominations.any? {|name| mail.subject.downcase =~ /\b#{name}\b/}
            _a.present mail.subject, href: href
          else
            _a.missing mail.subject, href: href
          end
        end
      end
    end
  end
end

# produce JSON output of reports
_json do
  _ reports do |mail|
    _subject mail.subject
    _link MBOX + URI.escape('<' + mail.message_id + '>')
    _missing missing.any? {|title| mail.subject.downcase =~ /\b#{title}\b/}
  end
end
