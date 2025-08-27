document.getElementById('analyze-button').addEventListener('click', async () => {
    const hadithText = document.getElementById('hadith-input').value.trim();
    if (!hadithText) {
        alert('Please enter Hadith text to analyze.');
        return;
    }

    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';
    resultsSection.innerHTML = '<div class="spinner-container"><div class="spinner"></div><p>Loading...</p></div>';

    try {
        const response = await fetch('/api/analysis/complete-analysis/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ hadith_text: hadithText }),
        });

        if (!response.ok) {
            throw new Error('Failed to get analysis results.');
        }

        const data = await response.json();
        renderResults(data);
    } catch (error) {
        console.error('Error fetching analysis:', error);
        resultsSection.innerHTML = `<p class="error">An error occurred while fetching the analysis. Please try again later.</p>`;
    }
});

let manualResultsData = {};

function renderResults(data) {
    manualResultsData = data.manual_search_results;
    const resultsSection = document.getElementById('results-section');
    resultsSection.innerHTML = '';

    // Display Hadith Content
    resultsSection.innerHTML += `
        <div class="result-block">
            <h3>Hadith Content</h3>
            <p>${data.hadith_content}</p>
        </div>
    `;

    // Display Narrators
    resultsSection.innerHTML += `
        <div class="result-block">
            <h3>Narrators</h3>
            <p><strong>All Narrators:</strong> ${data.narrators.join(', ')}</p>
            <p><strong>Existing Narrators:</strong> ${data.existing_narrators.join(', ')}</p>
            <p><strong>Missing Narrators:</strong> ${data.missing_narrators.join(', ')}</p>
        </div>
    `;

    // Display Found Keywords
    resultsSection.innerHTML += `
        <div class="result-block">
            <h3>Found Keywords</h3>
            <p>${data.found_keywords.join(', ')}</p>
        </div>
    `;

    // Display Manual Search Results
    resultsSection.innerHTML += `
        <div class="result-block">
            <h3>Keywords Search Results (Quran-Corpus-Dictionary-Based)</h3>
            ${renderManualResults(data.manual_search_results)}
        </div>
    `;

    // Display AI Search Results
    resultsSection.innerHTML += `
        <div class="result-block">
            <h3>AI Search Based Results (BM25)</h3>
            ${renderAiResults(data.ai_search_results)}
        </div>
    `;
}

function renderManualResults(manualResults) {
    let html = '';
    for (const keyword in manualResults) {
        const results = manualResults[keyword];
        if (results.length === 0) {
            html += `<h4>Results for "${keyword}"</h4><p>No manual results found.</p>`;
            continue;
        }

        const resultId = `manual-result-${keyword.replace(/\s+/g, '-')}`;
        html += `
            <h4>Results for "${keyword}"</h4>
            <div id="${resultId}" class="keyword-result-container">
                ${renderManualResult(results[0])}
            </div>
            ${results.length > 1 ? `
                <div class="pagination-controls">
                    <button class="prev-btn" onclick="changeManualResult('${resultId}', -1, '${keyword}')" disabled>&laquo; Prev</button>
                    <span class="page-info">1 / ${results.length}</span>
                    <button class="next-btn" onclick="changeManualResult('${resultId}', 1, '${keyword}')">Next &raquo;</button>
                </div>
            ` : ''}
        `;
    }
    return html;
}

function renderManualResult(result) {
    const occurrencesHtml = result.occurrences.map(occ => `
        <div class="ayah-item">
            <p class="ayah-reference">${occ.verse_reference}</p>
            <p class="ayah-arabic">${occ.arabic_text}</p>
            <p class="ayah-english">${occ.english_translation}</p>
        </div>
    `).join('');

    return `
        <div class="keyword-result">
            <p><strong>Keyword:</strong> ${result.keyword_text} (${result.meaning})</p>
            <p><strong>Description:</strong> ${result.description}</p>
            <p><strong>Total Occurrences:</strong> ${result.total_occurrences}</p>
            <div class="occurrences-container">
                ${occurrencesHtml}
            </div>
        </div>
    `;
}

function changeManualResult(resultId, direction, keyword) {
    const results = manualResultsData[keyword];
    const container = document.getElementById(resultId);
    const paginationControls = container.nextElementSibling;
    const pageInfo = paginationControls.querySelector('.page-info');
    const prevBtn = paginationControls.querySelector('.prev-btn');
    const nextBtn = paginationControls.querySelector('.next-btn');

    let currentIndex = parseInt(pageInfo.textContent.split(' / ')[0]) - 1;
    currentIndex += direction;

    container.innerHTML = renderManualResult(results[currentIndex]);

    pageInfo.textContent = `${currentIndex + 1} / ${results.length}`;
    prevBtn.disabled = currentIndex === 0;
    nextBtn.disabled = currentIndex === results.length - 1;
}

function renderAiResults(aiResults) {
    let html = '';
    for (const keyword in aiResults) {
        html += `<h4>Results for "${keyword}"</h4>`;
        html += '<div class="occurrences-container">';
        aiResults[keyword].forEach(result => {
            html += `
                <div class="ayah-item">
                    <p class="ayah-arabic">${result.arabic_diacritics}</p>
                    <p class="ayah-english">${result.english_translation}</p>
                    <p><strong>Surah:</strong> ${result.surah_name_english}, Ayah: ${result.aya_number}</p>
                    <p><strong>Score:</strong> ${result.score.toFixed(2)}</p>
                </div>
            `;
        });
        html += '</div>';
    }
    return html;
}
