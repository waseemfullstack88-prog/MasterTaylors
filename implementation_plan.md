# Master Taylor's Mobile App Plan

Build a lightweight, offline-capable mobile application for Master Taylor's that runs on any Android phone.

## User Review Required

> [!IMPORTANT]  
> Because compiling a native `.apk` file requires a massive download (Android Studio & Java SDKs), **I propose building this as a Progressive Web App (PWA)**. 
> 
> A PWA is built with standard web code (HTML/JS) but runs entirely **offline** on your phone. You simply open it once in Google Chrome on your Android, tap "Add to Home Screen", and it instantly installs as an app icon on your phone! It will look and feel exactly like a native Android app.

**Are you okay with this approach?** (If you strictly need a raw `.apk` file instead, let me know, and I can give you instructions on how to use a free online converter to turn this code into an `.apk`).

## Proposed Changes

We will create a new folder `MasterTaylorsMobile` with the following files:

### 1. The App Interface
#### [NEW] `index.html`
The main screen of the app. It will use a clean, **Light Theme** following Android Material Design guidelines. It will feature:
- A top header with the shop name.
- A prominent "Add Customer" floating action button.
- A search bar fixed near the top.
- A scrollable list of customers.

### 2. Styling (Light Theme)
#### [NEW] `styles.css`
- A clean white and light-grey color palette.
- Gold accents to match the shop's branding.
- Mobile-optimized touch targets (large buttons, readable fonts).

### 3. Application Logic
#### [NEW] `app.js`
- **Data Storage**: Uses the phone's built-in `localStorage` to save customer data permanently and offline.
- **Auto-Serial**: When opening the "Add Customer" form, it will find the highest serial number and automatically suggest the next one (while allowing you to edit it).
- **Search Logic**: Real-time filtering by Name, Phone, or Serial Number.
- **Backup & Restore (Data Safety)**: Since data is stored on the phone, we will add a simple Backup feature. You can click "Export Backup" to download a small file containing all your customers. You can email this file to yourself or save it to Google Drive. If you ever lose your phone, simply download the file on your new phone and click "Restore Backup" to instantly get all your customers back!

### 4. Android App Manifest
#### [NEW] `manifest.json` & Service Worker
These files are the secret sauce that tells Android "this is an installable mobile app" and caches all the files so it works completely without the internet.

## Verification Plan

1. I will write the HTML/CSS/JS code and save it in a new folder.
2. I will write a simple `run.bat` file that starts a local server on your computer.
3. You will scan a QR code (or type an IP address) into your Android phone's browser.
4. You will install it to your phone's home screen and test adding and searching customers offline!
