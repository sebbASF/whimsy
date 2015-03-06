Preface
---

 * I ask that you [give it five minutes](https://signalvnoise.com/posts/3124-give-it-five-minutes).
 * Be prepared to [rethink best practices](https://www.youtube.com/watch?v=x7cQ3mrcKaY).

The ASF manages its board meetings via a text file that contains the agenda
for the meeting.  PMC reports, comments on those reports, and action items
associated with those PMCs are stored in separate places in that text file.
The agenda tool brings this data together and makes it easier to both
navigate and update that file.

Preparation
---

This has been tested to work on Mac OSX and Linux.  It likely will not work
yet on Windows.

For a partial installation, all you need is Ruby and Node.js.

For planning purposes, prereqs for a _full_ installation will require:

 * A SVN checkout of
  [board](https://svn.apache.org/repos/private/foundation/board).

 * A directory, preferably empty, for work files containing such things as
  uncommitted comments.

 * The following software installed:
     * Subversion
     * Ruby 1.9.3 or greater
     * io.js plus [npm](https://www.npmjs.com/) install react, jsdom, and jquery
     * [PhantomJS](http://phantomjs.org/) 2.0
         * Mac OS/X Yosemite users may need to get the binary from comments
           on [12900](https://github.com/ariya/phantomjs/issues/12900).

Note:

 * The installation of PhantomJS on Linux current requires a 30+ minute
   compile.  The binary provided for OS/X Yosemite is not part of the
   standard distribution.  Feel free to skip this step on your first
   ("give it five minutes") pass through this.  If you see promise,
   come back and complete this step.


Kicking the tires
---

Run the following commands in a Terminal window:

    sudo gem install bundler
    git clone ...
    cd agenda
    bundle install
    rake spec
    rake server:test

Visit [http://localhost:9292/](http://localhost:9292/) in your favorite browser.

Notes:

 * If you don't have PhantomJS installed, or have a version of PhantomJS
   prior to version 2.0 installed, one test will fail. 

 * If you don't have io.js installed, two additional tests will fail.

 * The data you see is a sanitized version of actual agendas that have
   been included in the repository for test purposes.


Viewing Source (Live Results)
---

At this point, you have something up and running.  Let's take a look around.

 * The first thing I want you to do is use the view source function in your
   browser.  What you will see is:

     * A head section that pulls in some stylesheets.  Most notably, the
       stylesheet from [bootstrap](http://getbootstrap.com/).

     * a `<div>` element with an id of `main` followed by the HTML used
       to present the first page fetched from the server.  If you want to
       see a different page, go to that page and hit refresh then view
       source again.  This content is nicely indented and other than
       an abundance of `data-reactid` attributes that React uses to keep
       track of things, it is fairly straightforward.

    * a few `<script>` elements that pull in react, jquery, bootstrap, and
      the agenda app itself.  I suggest that you leave that for the moment,
      we'll come back to it.

    * an inline script that calls `React.render` with a datastructure
      containing all the data the app needs on the client to do navigation.
      Most importantly, this page contains a parsed agenda.   Mentally file
      that away for later consideration.

 * Next I want you to find and launch your browser's JavaScript console.  In
   it, enter the following expression: `Main.item`.  If you are currently on
   the agenda page, the results will be underwhelming.  If so, go to another
   page, and try again.  You will see the data associated with the specific
   page you are looking at.  Instance variables will be preceded by an
   underscore.  Methods and computed properties will not be.

 * If you are so inclined, you can actually make changes to the
   datastructures.  Those changes won't be visible until you re-render.
   Something to try: `Main.item._report = 'All is Good!'; Main.refresh()`

 * One last thing before we leave this section, go to an agenda page, and
   replace the final `/` in the URL with `.json`.  The contents you see is
   what is fetched by the client when it needs to get an update of the data.
   This data is heavily cached on both the client and server, so it takes
   negligible resources to check for updates.

Viewing Source (this time, Actual Code)
---

 * While you are unlikely to need to look at it, the agenda parsing logic
   is in [agenda.rb](https://svn.apache.org/repos/infra/infrastructure/trunk/projects/whimsy/lib/whimsy/asf/agenda.rb)
   plus the [agenda](https://svn.apache.org/repos/infra/infrastructure/trunk/projects/whimsy/lib/whimsy/asf/agenda)
   subdirectory.

 * the `views/pages/index.js.rb` file contains the code for the agenda page.
   It defines a class with a render method.  Names that start with an 
   underscore become HTML elements.  Nesting is generally represented by
   `do`...`end` blocks, and occasionally (rarely) by curly braces.  Attributes
   are represented by `name: value` pairs.  Note the complete lack of
   `<%=` ... `%>` syntax required by things like JSP or erb.  Iteration is
   done by naming what you want to iterate over, and following the do with
   a name in vertical bars that contains the instance.

   Element names that start with a capital letter are essentially macros.
   We'll come back to that.

 * the `views/pages/search.js.rb` file contains the code for the search page.
   There are more methods defined here.  You will find definitions for
   these methods in the React 
   [Lifecycle Methods](http://facebook.github.io/react/docs/component-specs.html#lifecycle-methods).
   You will see logic mixed with presentation.  React is deadly serious when
   it adopted the slogan "rethink best practices".  What makes this work
   is the component lifecycle that React provides.  Components have mutable
   state (which are the variables which are preceded by an `@` sign), and are
   passed immutable properties (variables preceded by two `@` signs).  Some
   methods are prohibited from mutating state (most notable: the render
   method).  And one method (`componentWillReceiveProps`) even has access
   to the before and after values for properties.  Don't get hung up on the
   logic here, but do go to the navigation bar on the top right of the
   browser page, and select `Search` and play with search live.
 
 * At this point, I suggest that you make a change.  More specifically, I
   suggest you break something.  Insert the keyword `do` into a random spot
   in either this or another file, and save your changes.  This will cause
   the server to restart.  Hit refresh in the browser, and you will see
   a stack traceback indicating where the problem is.  Undo this change,
   and then lets continue exploring.

 * The `views/forms/add-comment.js.rb` file is probably a better example of
   a component.  The render function is more straightforward.  Not mentioned
   before, but element names followed by a dot followed by a name is a
   shorthand for specifying HTML class attributes.  And an element name
   followed by a dot followed by an exclamation point is shorthand for
   specifying HTML id attributes.  Both of these innovations were first
   pioneered by [markaby](http://markaby.github.io/).

   Of special interest in this file is the `onChange` and `onClick`
   attributes.  This is how you associate an event with a method.  The
   `save` method will call post which will send data to the server.

 * `views/actions/comment.json.rb` is the code which is run on the server
   when you save a comment.  It gets a list of pending items for this user,
   modifies it based on the parameters passed, puts this data back and then
   returns the modified list to the client (this is the last line, in Ruby
   the keyword `return` is optional, and generally not used unless returning
   from the middle of a method).  Most server actions will be simple.  Some
   will do things like commit changes to svn.

 * I mentioned previously that element names that start with a capital
   letter are effectively macros.  You've seen `Index`, `Search`, and
   `AddComment` classes, each of which start with a capital letter.  These
   actually are examples of what React calls components that act like
   macros.  `views/main.html.rb' contains the 'top'.  `views/app.js.rb`
   lists all of the files that make up the client side of the application.

 * This brings us back to to the app.js script mentioned much earlier.
   If you visit http://localhost:9292/app.js you will see the full script. 
   Every bit of this JavaScript was generated from the js.rb files mentioned
   above.  Undoubtedly you have seen small amounts of JavaScript before
   but I suspect that much of this looks foreign.  Nicely indented,
   vaguely familiar, but very foreign.  Most people these days generate
   JavaScript.  Popular with React is something called JSX, but that's
   both controversial and [doesn't support if
   statements](http://facebook.github.io/react/tips/if-else-in-JSX.html).

Testing
---

If you've made it this far, you've undoubtedly spent more than the five
minutes I've asked of you.  Hopefully, that's because I've piqued your
interest.  Having a test suite is important as it will allow you to
confidently make changes without breaking things.  If you haven't yet,
I encourage you to install Poltergeist and io.js.

Before running the tests, run `rake clobber` to undo any changes you
make have made by running the application.

Now onto the tests:

  * `spec/parse_spec.rb` is a vanilla unit test that verifies that the
    output of a parse matches what you would expect.  This approach is
    good testing out server side logic.

  * `spec/index_spec.rb`, and `report_spec.rb`, and `spec/other_views_spec.rb`
    uses [capybara](https://github.com/jnicklas/capybara) to verify that
    the html produced matches what you would expect.  This makes use of the
    server side rendering of pages.  Generally this involves identifying
    things to look for in the HTML with CSS paths and either text or
    attribute values.  Clearly this approach is focused on verifying HTML
    output.

  * `spec/form_spec.rb` shows how client side logic (expressed in Ruby,
     but compiled to JavaScript) can be tested.  It does so by setting
     up a http server (the code for which is in `spec/react_server.rb`)
     which runs arbitrary scripts and returns the results as HTML.  This
     approach excels at testing a React component.

  * Finally, `spec/navigate_spec.rb` actually tests functions with a real
    (albeit headless) browser.

Despite the diversity, the above tests have a lot of commonality and build
on standard Ruby test functions.  Together they should be able to cover
pretty much any type of testing requirements.

Running for real
---

So far, you've run with test data.  If you want to run for real, you need
to have a recent checkout of
https://svn.apache.org/repos/private/foundation/board and a directory to
store pending updates.  If you have both, create a file named `.whimsy`
in your home directory.  The file format is YAML, and here is an excerpt
from mine:

    ---
    :svn:
    - /home/rubys/svn/foundation/board
    :agenda_work: /home/rubys/tmp/agenda

Adapt as necessary.  The `svn` entry is actually an array. Other whimsy apps
may use other svn directories.  `agenda_work` is a string.  Another relavant
entry that is not shown here is `lib`.  It is an array of libraries that
are to be used instead of gems you may have installed.  This is useful if
you are making changes to the agenda parsing logic, ruby2js or wunderbar.

With this in place, start the server with `rake server` instead of
`rake server:test`.  It will tell you what directories are being watched
for changes - this list includes libraries listed in the `.whimsy` file.
It will also tell you what svn directory and agenda work directories are
being used.


Conclusion
---

Congratulations for making it this far.  To recap:

 * You have gotten the whimsy agenda application running locally on your
   own laptop or desktop.  You've seen how to inspect and interact with
   the running code, and explored a number of representative functions.

 * You've made a change and saw it deployed immediately (even though the
   change was to break things).

 * You've run the tests, so you can confidently make changes and know that
   they didn't break anything.

 * Most of all, you've seen that things seems unreasonably fast without
   you needing to expend much effort to make it so.

This code clearly isn't complete.  What I'm looking for is people who are
wlling to experiment and contribute.  Are you in?

Gotchas
---

Nothing is perfect.  Here are a few things to watch out for:

 * In Ruby there isn't a difference between accessing attributes and methods
   which have no arguments.  In JavaScript there is.  To make this work,
   parenthesis are required when calling or defining methods that have
   no arguments.

 * In React, assignments to component state (@variables) don't take effect
   immediately.  You will find that individual methods tend to be short in
   React components, but if you find yourself assigning to a state variable
   and then reading it later in the same function you won't be seeing the
   updated value.

 * While I've provided a Gemfile to help with installation, `bundle exec`
   play nicely with `rake spec` or `rake server`.  I haven't spent the time
   to figure out why this is.

If you encounter any other gotchas, let me know and I'll update this README.

Further reading:
---

 * [bootstrap](http://getbootstrap.com/)
 * [capybara](https://github.com/jnicklas/capybara#readme)
 * [react](http://facebook.github.io/react/)
 * [ruby2js](https://github.com/rubys/ruby2js/#readme)
 * [phantomjs](http://phantomjs.org/)
 * [sinatra](http://www.sinatrarb.com/)
 * [wunderbar](https://github.com/rubys/wunderbar/#readme)
