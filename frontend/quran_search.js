document.getElementById('search-button').addEventListener('click', () => {
    const meaning = document.getElementById('keyword-input').value.trim();
    if (meaning) {
        displayAyahs(meaning);
    }
});

const dictionaryFiles = [
    'letter_$_ش.json', 'letter_A_أ.json', 'letter_b_ب.json', 'letter_d_د.json',
    'letter_D_ض.json', 'letter_f_ف.json', 'letter_g_غ.json', 'letter_H_ح.json',
    'letter_h_ه.json', 'letter_j_ج.json', 'letter_k_ك.json', 'letter_l_ل.json',
    'letter_m_م.json', 'letter_n_ن.json', 'letter_q_ق.json', 'letter_r_ر.json',
    'letter_s_س.json', 'letter_S_ص.json', 'letter_t_ت.json', 'letter_T_ط.json',
    'letter_v_ث.json', 'letter_w_و.json', 'letter_x_خ.json', 'letter_y_ي.json',
    'letter_z_ز.json', 'letter_Z_ظ.json'
];

let allKeywordsData = [];

async function loadAllData() {
    const promises = dictionaryFiles.map(file => 
        fetch(`/Storage/Quran Dictionary With English Translation/${file}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load ${file}`);
                }
                return response.json();
            })
    );
    
    try {
        const results = await Promise.all(promises);
        allKeywordsData = results.flat();
    } catch (error) {
        console.error("Error loading dictionary files:", error);
        const resultsSection = document.getElementById('results-section');
        resultsSection.innerHTML = `<p class="error">Error loading dictionary data. Please try again later.</p>`;
    }
}

async function displayAyahs(meaning) {
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';
    resultsSection.innerHTML = '<div class="spinner-container"><div class="spinner"></div><p>Loading...</p></div>';

    if (allKeywordsData.length === 0) {
        await loadAllData();
    }

    const matchingKeywords = allKeywordsData.filter(item => item.meaning && item.meaning.toLowerCase().includes(meaning.toLowerCase()));

    if (matchingKeywords.length > 0) {
        resultsSection.innerHTML = ''; 
        matchingKeywords.forEach(keywordData => {
            const keywordResultElement = document.createElement('div');
            keywordResultElement.classList.add('keyword-result');
            keywordResultElement.innerHTML = `
                <h3>Keyword: ${keywordData.keyword_text} (${keywordData.meaning})</h3>
                <p class="description">${keywordData.description}</p>
                <p class="occurrences">Total Occurrences: ${keywordData.total_occurrences}</p>
                <hr>
            `;
            
            keywordData.occurrences.forEach(occurrence => {
                const ayahElement = document.createElement('div');
                ayahElement.classList.add('ayah-item');
                ayahElement.innerHTML = `
                    <p class="ayah-arabic">${occurrence.arabic_text}</p>
                    <p class="ayah-english">${occurrence.english_translation}</p>
                `;
                keywordResultElement.appendChild(ayahElement);
            });
            resultsSection.appendChild(keywordResultElement);
        });
    } else {
        resultsSection.innerHTML = '<p>No results found for this meaning.</p>';
    }
}

// Pre-load the data when the page loads for faster searching
loadAllData();
