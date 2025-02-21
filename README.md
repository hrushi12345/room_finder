# Room Finder System

## Project Description

The Room Finder System helps users find personalized room suggestions based on their hotel name (region), accommodation type, and maximum cost. The model uses data collected from the web.

This web application is built using Flask, and it allows users to input their information via a user-friendly form. Based on this input, the system suggests multiple room options, including hotel name, region, and cost.

### Features:
- **User Input Form**: Users can enter the hotel name, accommodation type, and maximum cost.
- **Room Recommendation**: The system recommends rooms based on the user inputs.
- **Database Integration**: Data is stored in MySQL, using tables such as `UserAccount`, `UserProfile`, and `Room` to manage user information and recommendations.

## Tech Stack
- **Flask**: Web framework to handle requests and render HTML templates.
- **MySQL**: Database to store and retrieve user data.
- **Jinja2**: Templating engine used for rendering HTML in Flask.
- **Python**: The primary language used for developing the backend logic.
- **HTML/CSS**: For designing the user input form and the front-end interface.

## Setup Instructions

### Prerequisites

Make sure you have the following installed:
- **Python 3.12.3**
- **MySQL Server**

#### [Python 3.12 Setup Steps](https://www.python.org/downloads/release/python-3123/)
- Follow the link for installation steps and make sure to add Python to your system's PATH during installation.

#### [MySQL Setup Steps](https://dev.mysql.com/doc/refman/8.0/en/installing.html)
- Follow the link to set up the MySQL server on your system.

### Create Python Virtual Environment and Install Flask

1. Open the command line in the project folder.

2. To create a virtual environment:
   ```bash
   python -m venv env
   ```

3. To activate the environment:
   - On Windows:
     ```bash
     env\Scripts\activate
     ```

4. Install the required Python packages:
   ```bash
   pip install -r req.txt
   ```

### Set Up Database in MySQL

1. Open **MySQL Workbench** by searching for it in the Windows application tray.

2. In the **Menu bar**, click on **Database**.

3. Click **Connect to Database** and then click **OK**.

4. In the **Schemas** panel (on the left), you will see the list of databases.

5. Below the **View** menu, click the **+** button to create a new schema.

6. Enter the desired database name and click the **Apply** button at the bottom right.

7. The created schema should now appear in the left pane. Right-click on it and select **Set as Default Schema**.

### Update Database Credentials

1. Open the `config.json` file in your project folder.

2. Update the database credentials in the `config.json` file with the following information:
   ```json
   {
       "username": "your-mysql-username",
       "password": "your-mysql-password",
       "host": "localhost",
       "database": "room_finder"
   }
   ```

### Create Database Tables

1. In the project folder, activate the Python virtual environment by running:
   ```bash
   env\Scripts\activate
   ```

2. Run the `create_tables.py` script to create the necessary tables in your database:
   ```bash
   python create_tables.py
   ```

### Running the Project

Once the above steps are completed, run the Flask application:

1. In the project folder, make sure the environment is activated.

2. Run the application using:
   ```bash
   python app.py
   ```

3. Open your browser and go to `http://127.0.0.1:5000` to access the Room Finder form.

## Usage

1. Enter the required details such as hotel name, accommodation type, and maximum cost.
2. After submitting the form, the system will recommend suitable room options based on the provided data.

## Future Enhancements

- Improve the recommendation model with more accurate machine learning algorithms.
- Add a feature for users to save their recommendations and provide more personalized suggestions based on history.
- Add a room booking system.

## Contributing

Feel free to fork the repository, submit issues, and open pull requests with any improvements or features you would like to contribute!

## License

This project is licensed under the MIT License.

## Acknowledgments

- Flask Documentation: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- MySQL Documentation: [https://dev.mysql.com/doc/](https://dev.mysql.com/doc/)
