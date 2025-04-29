# alumni-student-engagement-system

## About the Project

The **Alumni-Student Engagement System** is a platform designed to foster meaningful connections between alumni and current students. It aims to provide a space for mentorship, networking, and collaboration, enabling students to gain insights from alumni experiences and alumni to give back to their alma mater.

## Features

- **User Authentication**: Secure login and registration for both alumni and students.
- **Profile Management**: Users can create and update their profiles with relevant details such as education, work experience, and interests.
- **Mentorship Matching**: Intelligent matching system to connect students with alumni based on shared interests, career goals, and expertise.
- **Messaging System**: Built-in messaging feature for seamless communication between users.
- **Event Management**: Alumni and students can create, join, and manage events such as webinars, workshops, and networking sessions.
- **Resource Sharing**: A repository for sharing documents, articles, and other resources.

## Technologies Used

- **Frontend**: Jinja Templating
- **Backend**: Python Flask
- **Database**: MySQL
- **Authentication**: csrf

## Installation

1. Clone the repository:
    ```bash
    git clone git@github.com:Hillcrest01/alumni-student-engagement-system.git
    ```
2. Navigate to the project directory:
    ```bash
    cd alumni-student-engagement-system
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements. tx
    ```
4. Set up environment variables:
    - Create a `.env` file in the root directory.
    - Add the following variables:
      ```
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 
        'mysql://root:your_password@localhost/database_name?charset=utf8mb4')
      ```
5. Start the development server:
    ```bash
    python run.py
    ```

## Usage

1. Register as a student or alumni.
2. Complete your profile to enhance matching accuracy.
3. Explore the platform to find mentors, mentees, or events.
4. Use the messaging system to connect with others.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b feature/YourFeatureName
    ```
3. Commit your changes:
    ```bash
    git commit -m "Add your message here"
    ```
4. Push to the branch:
    ```bash
    git push origin feature/YourFeatureName
    ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For questions or feedback, please contact:
- **Project Maintainer**: [Your Name](mailto:your.peterochieng008@gmail.com)
- **GitHub Repository**: [GitHub Link](https://github.com/Hillcrest01/alumni-student-engagement-system)

## Acknowledgments

- Thanks to all contributors and testers.
- Special thanks to the alumni and students who provided valuable feedback during development.
- Inspired by the need for stronger alumni-student connections.