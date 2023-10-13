# Bookworm
#### Video: [Bookworm Demo Video](https://youtu.be/GAm8IEEmpKg)
#### Description:
Bookworm is a web application written using Python, HTML, and CSS. More specifically, it has been written using the Flask Python framework. Djinja was used to template the HTML pages. It has 10 HTML pages which are returned via routes in the Flask framework.


### Process:
Before Login:
-Users can create an account to begin and login to the application. The login page allows users to login or go to the forgot password page. The forgot password page resets the password of the certain user to "bookworm". And once the user logs in with the reset password, they are directly redirected to the change password page, so that they can change their password and to limit breaches of accounts. The register page allows users to make a username, password, and confirm the password.

Login:
-New users are directed to the set goal page. Users then have to set a goal. Existing users are led to their homepage. On the hompage, you will be able to see the user's goal, and how many books they have to read to reach the goal. Under that, books read and reviewed by other users will be suggested to the user.

After Login:
-Users can see their activity, give reviews for books they have read to reach their goal, and be suggested to read books read and reviewed by other users. On the activity page, you can see the user's actions. They will be able to see which books they have read and the reviews they have given for each book they read. The give review page allows users to input the title of the book they read, the author of the book, and their review of the book.Also, the application lets the user change their password. The change password page allows users to change their password to a new one. This page is alos used if the user logs in with the "bookworm" password, which is a standard password that users' passwords are reset to if they forget their unique password.

### HTML Files:
-layout.html: This is the HTML page used as the layout for the website. Jinja was used to extend this HTML page.
-activity.html: This is the HTML page that shows the user's activities. They will be able to see the title of the books they read, alongside the authors' name and the reviews they have wrote for each book they read.
-apology.html: This is the HTML page used to show an error. Whenever the user inputs an invalid input into a HTML form, this HTMl page is used to show the error made to the user.
-change.html: This is the HTML page used to change a user's password. This page has a HTML form that POSTS the new password and the password in the "users" table is changed to the new password.
-forgot.html: The HTMl page that has a HTML form to retrieve user's username and reset their password to "bookworm" if they have forgotten their unique password.
-form.html: This HTML page is used to show a form, using a HTML form, in which users can input the title, author, and the review of the book they finished reading.
-goal.html: This is the HTML page used to set a user goal of books to read. Based on this value and the books the user has read(which is checked via the inputs of books), the header under the 1st header changes.
-index.html: This is the HTML page that shows the user's goal, 2 sentences to show the user how many more books to read and a supportive message, and a section which shows books read by other users and those books' reviews. This is basically the homepage.
-login.html: This is the HTML page to log into the application. It also iuncludes a button for users who forgot their password.
-register.html: The HTML page for registering a username and a password, and confirming the password. This page posts the form and input the user input into the database.

### Contemplated design:
-In the beginning, I thought of using an API from a worldwide literature database. This was to create a application in which users could input ISBN numbers instead of having to input title and author all the time. Also, I thought of implementing an API which would allow users to get the summary of a book by searching up the book's title. I couldn't do this because the API was paid and the free APIs didn't let me find works based on title. If I could have implemented an API to a ISBN server, it would have allowed to add pages where users could search for books, learn about books, and see the books' summaries and cover page.

### Potential Improvements:
-There are some potential new features I could add to the web application. I could add a chat room for users, an ability to friend other users, the ability for users to add books to their list of favorite books, the ability to upvote other users' reviews on a book, a system where books are suggested based on the user's favorite genres(which they input themselves), and a search engine in which users can search for books read and reviewed by other users. The search engine would use SQL queries and would pass an input into the API link to get the output of the information(in json) of the book.

This web application is for the book-reading community. They will be able to help with each other anonymously and safely. Users can give honest reviews based on their own thoughts and views, helping other users pick books to read based on honest reviews and unbiased reviews.
