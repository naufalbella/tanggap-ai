# TanggapAI Frontend

Modern web interface for the TanggapAI customer feedback analyzer.

## 🎨 Features

-   **Feedback Analysis Form**: Submit customer feedback for instant AI-powered analysis
-   **Real-Time Results Display**: View sentiment, category, priority, keywords, root cause, and recommendations
-   **Historical Data Table**: Browse past analyses with advanced filtering
-   **Responsive Design**: Works on desktop, tablet, and mobile devices
-   **Modern UI/UX**: Clean interface with gradient headers, card-based layout, and smooth animations

## 📁 Files

```
frontend/
├── index.html      # Main HTML structure
├── style.css       # Styling and responsive design
├── app.js          # JavaScript for API integration
├── nginx.conf      # Nginx configuration for Cloud Run
├── Dockerfile      # Container definition
└── deploy.sh       # Deployment script
```

## 🚀 Quick Start

### Local Development

#### Option 1: Python HTTP Server

```bash
python -m http.server 3000
```

Then open http://localhost:3000

#### Option 2: Node.js HTTP Server

```bash
npx http-server -p 3000
```

#### Option 3: VS Code Live Server

Install the "Live Server" extension and click "Go Live" in the bottom right.

### Configuration

Update the backend URL in `app.js` if needed:

```javascript
const CONFIG = {
    API_BASE_URL: "http://localhost:8080", // Your backend URL
};
```

## 🌐 Deployment

Deploy to Google Cloud Run:

```bash
./deploy.sh
```

This script will:

1. Get the backend URL from Cloud Run
2. Deploy the frontend container
3. Configure environment variables
4. Display the frontend URL

### Manual Deployment

```bash
gcloud run deploy tanggap-ai-frontend \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1
```

## 🎯 Usage

### Analyze Feedback

1. Enter customer feedback in the text area
2. Click "Analyze Feedback"
3. View the analysis results:
    - **Sentiment**: Positive, Neutral, or Negative
    - **Category**: Delivery, Product, Service, Payment, or Technical
    - **Priority**: 1-5 urgency score
    - **Keywords**: Key terms extracted from feedback
    - **Root Cause**: Identified underlying issue
    - **Recommendation**: Actionable solution
    - **Summary**: One-sentence overview

### View History

1. Browse the feedback history table
2. Use filters to narrow results:
    - Filter by sentiment (positive/neutral/negative)
    - Filter by category (delivery/product/service/payment/technical)
3. Click "Refresh" to reload the latest data

## 🎨 Customization

### Colors

Edit `style.css` to customize colors:

```css
:root {
    --primary-color: #4f46e5; /* Primary brand color */
    --success-color: #10b981; /* Positive sentiment */
    --warning-color: #f59e0b; /* Medium priority */
    --danger-color: #ef4444; /* Negative sentiment */
}
```

### Layout

Modify `index.html` to change the layout structure.

### Functionality

Update `app.js` to add new features or modify API calls.

## 🔧 Technical Details

### Technologies Used

-   **HTML5**: Semantic markup
-   **CSS3**: Modern styling with CSS Grid and Flexbox
-   **Vanilla JavaScript**: No frameworks, pure JS for simplicity
-   **Nginx**: Production web server
-   **Docker**: Containerization for deployment

### Browser Support

-   Chrome/Edge: Latest 2 versions
-   Firefox: Latest 2 versions
-   Safari: Latest 2 versions
-   Mobile browsers: iOS Safari, Chrome Mobile

### Performance

-   Gzip compression enabled
-   Static asset caching (1 year)
-   Minimal JavaScript bundle
-   No external dependencies

## 📱 Responsive Breakpoints

-   **Desktop**: > 768px
-   **Tablet**: 481px - 768px
-   **Mobile**: < 480px

## 🐛 Troubleshooting

### Backend Connection Issues

If you see "Backend not reachable" in the console:

1. Check that backend is running
2. Verify CORS is enabled in backend
3. Update `API_BASE_URL` in `app.js`

### CORS Errors

The backend already has CORS enabled. If you still see errors:

1. Check that backend allows your frontend origin
2. Verify the backend URL is correct
3. Check browser console for specific error messages

### Deployment Issues

If deployment fails:

1. Ensure you're logged in: `gcloud auth login`
2. Set project: `gcloud config set project YOUR_PROJECT_ID`
3. Enable Cloud Run API
4. Check that backend is deployed first

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please ensure:

1. Code follows existing style
2. Test on multiple browsers
3. Maintain responsive design
4. Keep JavaScript vanilla (no frameworks)

---

**Part of TanggapAI - Enterprise Customer Feedback Analyzer**
