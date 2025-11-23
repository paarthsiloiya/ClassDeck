Quick Start Guide
=================

Welcome to ClassDeck! This guide will help you get up and running with your personal Google Classroom command center.

Prerequisites
-------------

Before you begin, ensure you have the following installed:

*   Python 3.8 or higher
*   A Google Cloud Project with the Classroom API enabled
*   `client_secret.json` file from your Google Cloud Project

Installation
------------

1.  **Clone the repository:**

    .. code-block:: bash

        git clone https://github.com/paarthsiloiya/ClassDeck.git
        cd ClassDeck

2.  **Install dependencies:**

    .. code-block:: bash

        pip install -r requirements.txt

3.  **Configure Environment:**

    Create a `.env` file in the root directory (optional, but recommended for secrets):

    .. code-block:: bash

        SECRET_KEY=your-secret-key-here
        OAUTHLIB_INSECURE_TRANSPORT=1  # Only for local development

4.  **Setup Google Credentials:**

    Place your `client_secret.json` file in the root directory of the project.

5.  **Initialize the Database:**

    Run the initialization script to create the local database:

    .. code-block:: bash

        python init_db.py

Running the Application
-----------------------

Start the Flask development server:

.. code-block:: bash

    python run.py

Open your browser and navigate to `http://127.0.0.1:5000`. You will be prompted to log in with your Google account.

Features
--------

*   **Dashboard**: View all your active classes in a grid or list view.
*   **Stream**: See announcements, assignments, and materials for each class.
*   **Missing Assignments**: Track overdue work across all your classes.
*   **Customization**: Rename classes, change banners, and add tags to organize your workflow.
*   **Dark Mode**: Toggle between light and dark themes for comfortable viewing.
