const API_URL = 'http://localhost:5000/api/search';

async function search() {
    const query = document.getElementById('query').value.trim();
    if (!query) {
        showError('Please enter a search query');
        return;
    }

    const resultsDiv = document.getElementById('results');
    resultsDiv.className = 'results show';
    resultsDiv.innerHTML = '<div class="loading"><span class="spinner"></span>Searching...</div>';

    try {
        const response = await fetch(`${API_URL}?query=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (!response.ok) {
            showError(data.message || 'Error: ' + response.status);
            return;
        }

        displayResults(data);
    } catch (error) {
        showError('Could not connect to server. Make sure Docker is running.');
    }
}

function showError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.className = 'results show';
    resultsDiv.innerHTML = `<div class="error">⚠️ ${message}</div>`;
}

function displayResults(data) {
    const { professor, department, course_id, data: courseData } = data;
    const rmp = courseData.rmp;
    const reddit = courseData.reddit;

    // RMP section
    let rmpHtml = '';
    if (rmp.found) {
        rmpHtml = `
            <div class="rating-grid">
                <div class="rating-item">
                    <div class="rating-label">Overall Rating</div>
                    <div><span class="rating-value">${rmp.average_rating.toFixed(1)}</span><span class="rating-max">/ 5.0</span></div>
                </div>
                <div class="rating-item">
                    <div class="rating-label">Difficulty</div>
                    <div><span class="rating-value">${rmp.average_difficulty.toFixed(1)}</span><span class="rating-max">/ 5.0</span></div>
                </div>
            </div>`;
    } else {
        rmpHtml = `<p class="no-data">No Rate My Professor data found for ${professor}</p>`;
    }

    // Reddit section
    let redditHtml = '';
    if (reddit.found && reddit.posts.length > 0) {
        const postsHtml = reddit.posts.map(post => {
            return post.post_url
                ? `<li><a href="${post.post_url}" target="_blank" rel="noopener noreferrer">${post.title}</a></li>`
                : `<li>${post.title}</li>`;
        }).join('');

        redditHtml = `<ul class="reddit-list">${postsHtml}</ul>`;
    } else {
        redditHtml = `<p class="no-data">No Reddit discussions found for ${department.toUpperCase()} ${course_id}</p>`;
    }

    const neitherBanner = !rmp.found && !reddit.found
        ? `<div class="no-data-banner">⚠️ No Rate My Professor or Reddit data found for this search.</div>`
        : '';

    document.getElementById('results').innerHTML = `
        <div class="result">
            ${neitherBanner}
            <div class="result-header">
                <h2>
                    <span class="professor-name">${professor.toUpperCase()}</span>
                    <span class="course-code">${department.toUpperCase()} ${course_id}</span>
                </h2>
            </div>
            <div class="section">
                <div class="section-title">⭐ Rate My Professor</div>
                ${rmpHtml}
            </div>
            <div class="section">
                <div class="section-title">💬 Reddit Discussions (r/VirginiaTech)</div>
                ${redditHtml}
            </div>
        </div>`;
}