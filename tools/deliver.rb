#
# Receive and deliver mail
#

require 'digest'
require 'time'
require 'fileutils'

MAIL_ROOT = '/srv/mail'

# get the message ID
def self.getmid(hdrs)
  mid = hdrs[/^Message-ID:.*/i]
  if mid =~ /^Message-ID:\s*$/i # no mid on the first line
    # capture the next line and join them together
    mid = hdrs[/^Message-ID:.*\r?\n .*/i].sub(/\r?\n/,'')
  end
  mid
end

mail = STDIN.read.force_encoding('binary')

# extract info
dest = mail[/^List-Id: <(.*)>/, 1] || mail[/^Delivered-To.* (\S+)\s*$/, 1] || 'unknown'
time = Time.parse(mail[/^Date: (.*)/, 1]) rescue Time.now
hash = Digest::SHA1.hexdigest(getmid(mail) || mail)[0..9]

# build file name
file = "#{MAIL_ROOT}/#{dest[/^[-\w]+/]}/#{time.strftime("%Y%m")}/#{hash}"

File.umask 0002
FileUtils.mkdir_p File.dirname(file)
File.write file, mail, encoding: Encoding::BINARY
File.utime time, time, file
File.chmod 0644, file
