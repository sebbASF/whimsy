#
# This is the client model for draft Minutes.
#

class Minutes
  @@list = {}

  # (re)-load minutes
  def self.load(list)
    @@list = {}

    if list
      for title in list
        @@list[title] = list[title]
      end
    end
  end

  def self.actions
    actions = []

    for title in @@list
      minutes = @@list[title] + "\n\n"
      pattern = RegExp.new('^(?:@|AI\s+)(\w+):?\s+([\s\S]*?)(\n\n|$)', 'gm')
      match = pattern.exec(minutes)
      while match
        actions << {owner: match[1], text: match[2], 
          item: Agenda.find(title.gsub(/\W/, '-'))}
        match = pattern.exec(minutes)
      end
    end

    return actions
  end

  # fetch minutes for a given agenda item, by title
  def self.get(title)
    return @@list[title]
  end

  # return a list of actual or expected attendees
  def self.attendees
    rollcall = Minutes.get('Roll Call') || Agenda.find('Roll-Call').text
    pattern = Regexp.new('\n   ( [a-z]*[A-Z][a-zA-Z]*\.?)+', 'g')
    attendees = []
    while (match=pattern.exec(rollcall)) do
      attendees << match[0].sub(/^\s+/, '').split(' ').first
    end
    attendees.sort()
  end

  # return a list of directors present
  def self.directors_present
    rollcall = Minutes.get('Roll Call') || Agenda.find('Roll-Call').text
    rollcall[/Directors.*Present:\n\n((.*\n)*?)\n/,1].sub(/\n$/, '')
  end

  # determine if the meeting is over
  def self.complete
    Minutes.get('Adjournment')
  end

  # determine if the meeting is over
  def self.ready_to_post_draft
    self.complete and 
      not Server.drafts.include?  Agenda.file.sub('_agenda_', '_minutes_')
  end
end

Events.subscribe :minutes do |message|
  Minutes.load(message.value) if message.agenda == Agenda.file
end
