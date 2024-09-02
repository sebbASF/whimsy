#!/usr/bin/env ruby
PAGETITLE = "Member-only private list checks" # Wvisible:board,mail

$LOAD_PATH.unshift '/srv/whimsy/lib'
require 'wunderbar'
require 'wunderbar/bootstrap'
require 'whimsy/asf'
require 'whimsy/asf/mlist'

listname = ENV['QUERY_STRING']
listname = 'board' if listname == ''

info_chairs = ASF::Committee.load_committee_info.group_by(&:chair)
ldap_chairs = ASF.pmc_chairs
subscribers, modtime = ASF::MLIST.sub_digest('apache.org', listname)
subscribers ||= []
member_statuses = ASF::Member.member_statuses

_html do
  _body? do
    _whimsy_body(
      title: PAGETITLE,
      subtitle: 'How Subscribers Are Checked',
      relatedtitle: 'More Useful Links',
      related: {
        "/committers/tools" => "Whimsy Tool Listing",
        "/committers/subscribe" => "Committer Self-subscribe Tool",
        "/committers/moderationhelper" => "Mail List Moderation Helper",
        "https://github.com/apache/whimsy/blob/master/www#{ENV['SCRIPT_NAME']}" => "See This Source Code"
      },
      helpblock: -> {
        _h2 'DRAFT - may not be 100% accurate'
        _p! do
          _ "This script takes the list of subscribers (updated #{modtime}) to "
          _a "#{listname}@apache.org", "href: https://mail-search.apache.org/members/private-arch/#{listname}/"
          _ ' which are matched against '
          _a 'members.txt', href: ASF::SVN.svnpath!('foundation', 'members.txt')
          _ ', '
          _a 'iclas.txt', href: ASF::SVN.svnpath!('officers', 'iclas.txt')
          _ ', and '
          _code 'ldapsearch mail'
          _ ' to match each email address to an Apache ID.  '
          _br
          _ 'Those that are not found are listed as '
          _code.text_danger '*missing*'
          _ '.  Non ASF member, non-committee chairs are also '
          _span.text_danger 'listed in red'
          _ '.'
        end
        _p! do
          _ 'The resulting list is then cross-checked against '
          _a 'committee-info.text', href: ASF::SVN.svnpath!('board', 'committee-info.txt')
          _ ' and '
          _code 'ldapsearch cn=pmc-chairs'
          _ '.  Membership that is only listed in one of these two sources is '
          _span.text_danger 'listed in red'
          _ '.'
        end
      }
    ) do

      ids = []
      maillist = ASF::Mail.list
      subscribers.each do |line|
        person = maillist[line.downcase]
        person ||= maillist[line.downcase.sub(/\+\w+@/,'@')]
        if person
          id = person.id
          id = '*notinavail*' if id == 'notinavail'
        else
          person = ASF::Person.find('notinavail')
          id = '*missing*'
        end
        ids << [id, person, line]
      end

      _table_.table do
        _thead do
          _th 'ID'
          _th 'Email'
          _th 'Name'
          _th 'Committee'
        end
        _tbody do
          ids.sort.each do |id, person, email|
            status = member_statuses[person.name]
            next if status
            next if info_chairs.include? person or ldap_chairs.include? person
            _tr_ do
              href = "/roster/committer/#{id}"
              if id.include? '*'
                _td.text_danger id
              else
                _td.text_danger {_a id, href: href}
              end
              _td email

              if not id.include? '*'
                _td person.public_name
              else
                icla = ASF::ICLA.find_by_email(id)
                if icla
                  _td.text_danger icla.name
                else
                  _td.text_danger '*notinavail*'
                end
              end

              if info_chairs.include? person
                text = info_chairs[person].uniq.map(&:display_name).join(', ')
                if ldap_chairs.include? person or info_chairs[person].all? &:nonpmc?
                  _td text
                else
                  _td.text_danger text
                end
              elsif member_statuses[person.name]
                _td
              elsif ldap_chairs.include? person
                _td.text_danger '***LDAP only***'
              else
                pmcs = person.project_owners.map(&:name)
                if pmcs.length == 0
                  _td.text_danger '*** non-member, non-officer, non-pmc ***'
                else
                  _td.text_warning "*** non-member, non-officer, pmcs: #{pmcs.join ','} ***"
                end
              end
            end
          end
        end
      end
    end
  end
end
