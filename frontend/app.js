// Configuration
const CONFIG = {
    // Backend API URL - will be injected during deployment or use environment variable
    // For local development: http://localhost:8080
    // For production: set via BACKEND_URL environment variable or update manually
    API_BASE_URL:
        window.location.hostname === "localhost"
            ? "http://localhost:8080"
            : window.BACKEND_URL || "", // Will be set by deployment script
};

// API endpoints
const API = {
    ANALYZE: `${CONFIG.API_BASE_URL}/api/analyze`,
    QUERY: `${CONFIG.API_BASE_URL}/api/query`,
};

// DOM Elements
const feedbackForm = document.getElementById("feedbackForm");
const feedbackInput = document.getElementById("feedbackInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const btnText = document.querySelector(".btn-text");
const btnLoader = document.querySelector(".btn-loader");
const analysisResult = document.getElementById("analysisResult");
const errorMessage = document.getElementById("errorMessage");
const historyTable = document.getElementById("historyTable");
const filterSentiment = document.getElementById("filterSentiment");
const filterCategory = document.getElementById("filterCategory");
const refreshBtn = document.getElementById("refreshBtn");

// Result elements
const resultSentiment = document.getElementById("resultSentiment");
const resultCategory = document.getElementById("resultCategory");
const resultPriority = document.getElementById("resultPriority");
const resultKeywords = document.getElementById("resultKeywords");
const resultRootCause = document.getElementById("resultRootCause");
const resultRecommendation = document.getElementById("resultRecommendation");
const resultSummary = document.getElementById("resultSummary");

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    feedbackForm.addEventListener("submit", handleFormSubmit);
    refreshBtn.addEventListener("click", loadHistory);
    filterSentiment.addEventListener("change", loadHistory);
    filterCategory.addEventListener("change", loadHistory);
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();

    const feedback = feedbackInput.value.trim();
    if (!feedback) {
        showError("Please enter feedback text");
        return;
    }

    setLoading(true);
    hideError();
    hideResult();

    try {
        const response = await fetch(API.ANALYZE, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ feedback }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResult(data);

        // Reload history to show new entry
        setTimeout(() => loadHistory(), 500);

        // Clear form
        feedbackInput.value = "";
    } catch (error) {
        console.error("Analysis error:", error);
        showError(`Failed to analyze feedback: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

// Display analysis result
function displayResult(data) {
    // Update sentiment
    resultSentiment.textContent = data.sentiment;
    resultSentiment.className = `result-value sentiment-${data.sentiment}`;

    // Update category
    resultCategory.textContent = data.category;
    resultCategory.className = "result-value";

    // Update priority
    resultPriority.textContent = `${data.priority_score}/5`;
    resultPriority.className = `result-value priority-${data.priority_score}`;

    // Update keywords
    resultKeywords.innerHTML = data.keywords
        .map((keyword) => `<span class="keyword-tag">${keyword}</span>`)
        .join("");

    // Update details
    resultRootCause.textContent = data.root_cause;
    resultRecommendation.textContent = data.recommendation;
    resultSummary.textContent = data.summary;

    // Show result
    analysisResult.style.display = "block";

    // Smooth scroll to result
    analysisResult.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Load feedback history
async function loadHistory() {
    historyTable.innerHTML =
        '<div class="loading">Loading feedback history...</div>';

    try {
        // Build query parameters
        const params = new URLSearchParams();
        params.append("limit", "20");

        const sentiment = filterSentiment.value;
        if (sentiment) params.append("sentiment", sentiment);

        const category = filterCategory.value;
        if (category) params.append("category", category);

        const response = await fetch(`${API.QUERY}?${params.toString()}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success && data.data && data.data.length > 0) {
            displayHistory(data.data);
        } else {
            historyTable.innerHTML =
                '<div class="loading">No feedback found</div>';
        }
    } catch (error) {
        console.error("History load error:", error);
        historyTable.innerHTML = `<div class="loading" style="color: var(--danger-color);">Failed to load history: ${error.message}</div>`;
    }
}

// Display history table
function displayHistory(data) {
    const tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Feedback</th>
                    <th>Sentiment</th>
                    <th>Category</th>
                    <th>Priority</th>
                    <th>Root Cause</th>
                </tr>
            </thead>
            <tbody>
                ${data
                    .map(
                        (item) => `
                    <tr>
                        <td>${formatDate(item.created_at)}</td>
                        <td class="feedback-text" title="${escapeHtml(
                            item.feedback_text
                        )}">
                            ${escapeHtml(item.feedback_text)}
                        </td>
                        <td>
                            <span class="badge badge-${item.sentiment}">
                                ${item.sentiment}
                            </span>
                        </td>
                        <td>
                            <span class="badge badge-${item.category}">
                                ${item.category}
                            </span>
                        </td>
                        <td style="text-align: center;">${
                            item.priority_score
                        }</td>
                        <td style="max-width: 250px;">${escapeHtml(
                            item.root_cause
                        )}</td>
                    </tr>
                `
                    )
                    .join("")}
            </tbody>
        </table>
    `;

    historyTable.innerHTML = tableHTML;
}

// Utility functions
function setLoading(isLoading) {
    analyzeBtn.disabled = isLoading;
    btnText.style.display = isLoading ? "none" : "inline";
    btnLoader.style.display = isLoading ? "inline" : "none";
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = "block";
}

function hideError() {
    errorMessage.style.display = "none";
}

function hideResult() {
    analysisResult.style.display = "none";
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    };
    return date.toLocaleDateString("en-US", options);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Health check on load
async function checkBackendHealth() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/health`);
        if (response.ok) {
            console.log("✅ Backend connection successful");
        } else {
            console.warn("⚠️ Backend health check failed");
        }
    } catch (error) {
        console.error("❌ Backend not reachable:", error.message);
    }
}

// Run health check
checkBackendHealth();
