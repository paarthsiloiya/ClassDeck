# ClassDeck

ClassDeck is a personal Google Classroom dashboard designed for students who want more control, customization, and organization than the default Classroom interface provides.  
It adds a powerful **local layer of features** on top of the official Google Classroom data — without changing anything in the actual Google Classroom environment.

ClassDeck is built using **Flask**, **Python**, **Jinja templates**, and **Google Classroom APIs** (read-only scopes).  
No JavaScript is required for the core functionality.

---

## 🚀 Features

### 🎓 Enhanced Course Organization
- Locally rename **Classes**, **Class Codes**, and **Sections**
- Add custom **icons** and **banner images**
- Pin, unpin, or **archive any class**
- Change the appearance of class cards in a unified dashboard

### 📚 Assignment & Material Management
- View all assignments from all courses in one place
- Add **custom tags** (e.g., _HW_, _Exam_, _Important_)
- Mark assignments as **To Do**, **Doing**, or **Done**
- Add personal notes for any class or assignment

### 🗂️ Material Organization
- Categorize materials using tags and folders (e.g., Lectures, Tutorials, Books)
- Search materials by title, class, tag, or topic

### 📅 Calendar Integration
- Automatically add assignment due dates to **Google Calendar**
- Unified timeline of upcoming deadlines

### 🎨 UI Customization
- Google Classroom–style dashboard
- Local themes (Light, Dark, AMOLED)
- Clean grid layout using TailwindCSS
- All templates rendered with Jinja

### 🔐 Privacy & Security
- Uses **OAuth 2.0** (Google Sign-In)  
- Only requests **read-only Google Classroom scopes**
- Your customizations are stored **locally in your own database**
- Actual Classroom data is never modified

---

## 🛠️ Tech Stack

**Backend**
- Python 3  
- Flask  
- Google Auth / OAuth2  
- Google Classroom API (readonly scopes)

**Frontend**
- HTML + TailwindCSS  
- Jinja templating  
- Zero JavaScript required for core features

**Database**
- SQLite (development)  
- PostgreSQL / Firestore (optional for deployment)

---

## 🔑 Google API Configuration

To use ClassDeck, you must create a Google Cloud project and enable:

- **Google Classroom API**
- **Google Calendar API**

ClassDeck uses **OAuth Client ID**, not API keys.

---

## 📜 License

MIT License.

---

## ❤️ Acknowledgements

ClassDeck is not affiliated with Google.  
It simply uses their official APIs under standard OAuth2 permissions.

