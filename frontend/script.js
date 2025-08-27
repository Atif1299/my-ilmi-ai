document.addEventListener('DOMContentLoaded', () => {
    const hadithInput = document.getElementById('hadith-input');
    const resultsSection = document.getElementById('results-section');
    const buttons = {
        'complete-analysis': 'get_hadith_complete_info',
        'find-ayahs': 'get_hadith_related_ayahs',
        'extract-narrators': 'get_hadith_narators',
        'extract-content': 'get_hadith_content',
        'analyze-keywords': 'keyword_search',
        'highlight-keywords': 'highlight_keywords'
    };

    Object.keys(buttons).forEach(buttonId => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', () => handleAnalysis(buttonId));
        }
    });

    const toggleButtonLoading = (buttonId, isLoading) => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = isLoading;
            if (isLoading) {
                button.classList.add('loading');
            } else {
                button.classList.remove('loading');
            }
        }
    };

    // Utility function to convert **word** markdown to highlighted HTML
    const convertMarkdownHighlights = (text) => {
        if (!text) return text;
        return text.replace(/\*\*(.*?)\*\*/g, '<span class="highlighted-word">$1</span>');
    };

    const handleAnalysis = async (buttonId) => {
        const query = hadithInput.value.trim();
        if (!query) {
            showError('Please enter a Hadith to analyze.');
            return;
        }

        // Show loading only on clicked button
        toggleButtonLoading(buttonId, true);
        showLoading();

        try {
            const endpoint = buttons[buttonId];
            const startTime = performance.now();
            const response = await fetch(`/api/quran/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown server error' }));
                throw new Error(`Server error: ${response.status} - ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();
            const endTime = performance.now();
            const responseTime = Math.round(endTime - startTime);
            
            // Track analytics if available
            if (window.analyticsUtils) {
                window.analyticsUtils.incrementQueryCount();
                window.analyticsUtils.recordResponseTime(responseTime);
            }
            
            renderResults(data, buttonId.replace(/-/g, '_'));
        } catch (error) {
            showError(`Request Failed: ${error.message}`);
        } finally {
            toggleButtonLoading(buttonId, false);
        }
    };

    const showLoading = () => {
        resultsSection.innerHTML = '<div class="spinner-container"><div class="spinner"></div><p>Analyzing...</p></div>';
        resultsSection.style.display = 'block';
    };

    const showError = (message) => {
        resultsSection.innerHTML = `<div class="result-item error"><p><strong>Error:</strong> ${message}</p></div>`;
        resultsSection.style.display = 'block';
    };

    const renderResults = (data, resultType) => {
        resultsSection.innerHTML = '';
        resultsSection.style.display = 'block';
        
        const title = document.createElement('h2');
        resultsSection.appendChild(title);

        switch (resultType) {
            case 'complete_analysis':
                title.textContent = '🔍 Comprehensive Hadith Analysis';
                displayCompleteInfo(data);
                break;
            case 'find_ayahs':
                title.textContent = '📖 Related Quranic Ayahs';
                displayRelatedAyahs(data.results || data);
                break;
            case 'extract_narrators':
                title.textContent = '👥 Extracted Narrators';
                displayNarrators(data);
                break;
            case 'extract_content':
                title.textContent = '📜 Extracted Hadith Content';
                displayHadithContent(data.hadith_content || data);
                break;
            case 'analyze_keywords':
                title.textContent = '🔑 Keyword Search Results';
                displayKeywordSearchResults(data);
                break;
            case 'highlight_keywords':
                title.textContent = '✨ Keywords Highlighted in Text';
                displayHighlightedKeywords(data);
                break;
            default:
                resultsSection.innerHTML = '<div class="result-item error"><p>An unknown error occurred while rendering results.</p></div>';
        }
    };

    const createResultItem = (title, content) => {
        const item = document.createElement('div');
        item.className = 'result-item';
        if (title) {
            const itemTitle = document.createElement('h3');
            itemTitle.textContent = title;
            item.appendChild(itemTitle);
        }
        if (typeof content === 'string') {
            const itemContent = document.createElement('p');
            itemContent.innerHTML = content;
            item.appendChild(itemContent);
        } else {
            item.appendChild(content);
        }
        return item;
    };

    const displayCompleteInfo = (data) => {
        resultsSection.appendChild(createResultItem('📜 Extracted Hadith Content:', data.hadith_content || 'Not available.'));

        // Display narrators with existing/missing information
        const narratorsContainer = document.createElement('div');
        narratorsContainer.style.cssText = 'display: flex; flex-direction: column; gap: 1rem;';

        // Display existing narrators
        if (data.existing_narrators && data.existing_narrators.length > 0) {
            const existingSection = document.createElement('div');
            existingSection.style.cssText = 'padding: 1rem; background-color: #e8f5e8; border-left: 4px solid #4caf50; border-radius: 4px;';
            
            const existingTitle = document.createElement('h4');
            existingTitle.textContent = '✅ Existing Narrators in Database';
            existingTitle.style.cssText = 'margin: 0 0 0.5rem; color: #2e7d32; font-size: 1rem;';
            existingSection.appendChild(existingTitle);

            const existingList = document.createElement('ul');
            existingList.style.cssText = 'margin: 0; padding-left: 1.2rem;';
            data.existing_narrators.forEach(narrator => {
                const listItem = document.createElement('li');
                listItem.textContent = narrator;
                listItem.style.cssText = 'color: #2e7d32; margin-bottom: 0.25rem;';
                existingList.appendChild(listItem);
            });
            existingSection.appendChild(existingList);
            narratorsContainer.appendChild(existingSection);
        }

        // Display missing narrators
        if (data.missing_narrators && data.missing_narrators.length > 0) {
            const missingSection = document.createElement('div');
            missingSection.style.cssText = 'padding: 1rem; background-color: #fff3e0; border-left: 4px solid #ff9800; border-radius: 4px;';
            
            const missingTitle = document.createElement('h4');
            missingTitle.textContent = '⚠️ New Narrators (Not in Database)';
            missingTitle.style.cssText = 'margin: 0 0 0.5rem; color: #e65100; font-size: 1rem;';
            missingSection.appendChild(missingTitle);

            const missingList = document.createElement('ul');
            missingList.style.cssText = 'margin: 0; padding-left: 1.2rem;';
            data.missing_narrators.forEach(narrator => {
                const listItem = document.createElement('li');
                listItem.textContent = narrator;
                listItem.style.cssText = 'color: #e65100; margin-bottom: 0.25rem;';
                missingList.appendChild(listItem);
            });
            missingSection.appendChild(missingList);
            narratorsContainer.appendChild(missingSection);
        }

        // Summary
        const summarySection = document.createElement('div');
        summarySection.style.cssText = 'padding: 0.75rem; background-color: #f5f5f5; border-radius: 4px; font-size: 0.9rem; color: #666;';
        const totalNarrators = (data.narrators || []).length;
        const existingCount = (data.existing_narrators || []).length;
        const missingCount = (data.missing_narrators || []).length;
        summarySection.innerHTML = `
            <strong>Summary:</strong> 
            Total narrators found: ${totalNarrators} | 
            Existing in database: ${existingCount} | 
            New/Missing: ${missingCount}
        `;
        narratorsContainer.appendChild(summarySection);

        if (totalNarrators === 0) {
            narratorsContainer.innerHTML = '<p>No narrators found.</p>';
        }

        resultsSection.appendChild(createResultItem('👥 Extracted Narrators:', narratorsContainer));

        // Add section header for Related Ayahs
        const ayahsHeader = document.createElement('h3');
        ayahsHeader.innerHTML = '📖 Related Quranic Ayahs (with Highlighted Keywords)';
        ayahsHeader.style.cssText = 'margin: 2rem 0 1rem; color: var(--secondary-color); font-size: 1.3rem; font-weight: 600;';
        resultsSection.appendChild(ayahsHeader);

        // Use the new ayah display format
        if (data.related_ayahs && data.related_ayahs.length > 0) {
            data.related_ayahs.forEach((ayah, index) => {
                const ayahItem = document.createElement('div');
                ayahItem.className = 'ayah-item';
                
                const ayahHeader = document.createElement('div');
                ayahHeader.className = 'ayah-header';
                ayahHeader.innerHTML = `
                    <div class="ayah-reference">
                        <i class="fas fa-book-open"></i>
                        Surah ${ayah.surah_name_english} - Ayah ${ayah.aya_number}
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="ayah-score">Score: ${ayah.score.toFixed(2)}</div>
                        <i class="fas fa-chevron-down expand-icon"></i>
                    </div>
                `;
                
                const ayahContent = document.createElement('div');
                ayahContent.className = 'ayah-content';
                ayahContent.innerHTML = `
                    <div class="ayah-arabic">${ayah.arabic_diacritics || 'Arabic text not available'}</div>
                    <div class="ayah-english">${convertMarkdownHighlights(ayah.english_translation)}</div>
                `;
                
                ayahHeader.addEventListener('click', () => {
                    const isExpanded = ayahContent.classList.contains('expanded');
                    const icon = ayahHeader.querySelector('.expand-icon');
                    
                    if (isExpanded) {
                        ayahContent.classList.remove('expanded');
                        icon.classList.remove('rotated');
                    } else {
                        ayahContent.classList.add('expanded');
                        icon.classList.add('rotated');
                    }
                });
                
                ayahItem.appendChild(ayahHeader);
                ayahItem.appendChild(ayahContent);
                resultsSection.appendChild(ayahItem);
            });
        } else {
            const noAyahsMsg = document.createElement('div');
            noAyahsMsg.textContent = 'No related ayahs found.';
            noAyahsMsg.style.cssText = 'text-align: center; color: var(--light-text); padding: 2rem;';
            resultsSection.appendChild(noAyahsMsg);
        }

        const keywordsContainer = document.createElement('div');
        if (data.keywords && data.keywords.found_keywords && data.keywords.found_keywords.length > 0) {
            const keywordsHtml = data.keywords.found_keywords.map(kw => `<span class="keyword">${kw}</span>`).join(' ');
            keywordsContainer.innerHTML = `<p>Found ${data.keywords.total_keywords_found} unique keywords:</p>${keywordsHtml}`;
        } else {
            keywordsContainer.textContent = 'No keywords from the database were found in the related ayahs.';
        }
        resultsSection.appendChild(createResultItem('🔑 Keywords Found in Ayahs:', keywordsContainer));
    };

    const displayRelatedAyahs = (ayahs) => {
        if (ayahs && ayahs.length > 0) {
            ayahs.forEach((ayah, index) => {
                const ayahItem = document.createElement('div');
                ayahItem.className = 'ayah-item';
                
                const ayahHeader = document.createElement('div');
                ayahHeader.className = 'ayah-header';
                ayahHeader.innerHTML = `
                    <div class="ayah-reference">
                        <i class="fas fa-book-open"></i>
                        Surah ${ayah.surah_name_english} - Ayah ${ayah.aya_number}
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="ayah-score">Score: ${ayah.score.toFixed(2)}</div>
                        <i class="fas fa-chevron-down expand-icon"></i>
                    </div>
                `;
                
                const ayahContent = document.createElement('div');
                ayahContent.className = 'ayah-content';
                ayahContent.innerHTML = `
                    <div class="ayah-arabic">${ayah.arabic_diacritics || 'Arabic text not available'}</div>
                    <div class="ayah-english">${convertMarkdownHighlights(ayah.english_translation)}</div>
                `;
                
                ayahHeader.addEventListener('click', () => {
                    const isExpanded = ayahContent.classList.contains('expanded');
                    const icon = ayahHeader.querySelector('.expand-icon');
                    
                    if (isExpanded) {
                        ayahContent.classList.remove('expanded');
                        icon.classList.remove('rotated');
                    } else {
                        ayahContent.classList.add('expanded');
                        icon.classList.add('rotated');
                    }
                });
                
                ayahItem.appendChild(ayahHeader);
                ayahItem.appendChild(ayahContent);
                resultsSection.appendChild(ayahItem);
            });
        } else {
            resultsSection.appendChild(createResultItem(null, 'No related ayahs found.'));
        }
    };

    const displayNarrators = (data) => {
        // Handle both old format (array) and new format (object with existing/missing)
        if (Array.isArray(data)) {
            // Old format - just display the narrators
            if (data.length > 0) {
                const list = document.createElement('ul');
                data.forEach(narrator => {
                    const listItem = document.createElement('li');
                    listItem.textContent = narrator;
                    list.appendChild(listItem);
                });
                resultsSection.appendChild(createResultItem(null, list));
            } else {
                resultsSection.appendChild(createResultItem(null, 'No narrators found.'));
            }
        } else {
            // New format - display existing and missing narrators separately
            const narratorsContainer = document.createElement('div');
            narratorsContainer.style.cssText = 'display: flex; flex-direction: column; gap: 1rem;';

            // Display existing narrators
            if (data.existing_narrators && data.existing_narrators.length > 0) {
                const existingSection = document.createElement('div');
                existingSection.style.cssText = 'padding: 1rem; background-color: #e8f5e8; border-left: 4px solid #4caf50; border-radius: 4px;';
                
                const existingTitle = document.createElement('h4');
                existingTitle.textContent = '✅ Existing Narrators in Database';
                existingTitle.style.cssText = 'margin: 0 0 0.5rem; color: #2e7d32; font-size: 1rem;';
                existingSection.appendChild(existingTitle);

                const existingList = document.createElement('ul');
                existingList.style.cssText = 'margin: 0; padding-left: 1.2rem;';
                data.existing_narrators.forEach(narrator => {
                    const listItem = document.createElement('li');
                    listItem.textContent = narrator;
                    listItem.style.cssText = 'color: #2e7d32; margin-bottom: 0.25rem;';
                    existingList.appendChild(listItem);
                });
                existingSection.appendChild(existingList);
                narratorsContainer.appendChild(existingSection);
            }

            // Display missing narrators
            if (data.missing_narrators && data.missing_narrators.length > 0) {
                const missingSection = document.createElement('div');
                missingSection.style.cssText = 'padding: 1rem; background-color: #fff3e0; border-left: 4px solid #ff9800; border-radius: 4px;';
                
                const missingTitle = document.createElement('h4');
                missingTitle.textContent = '⚠️ New Narrators (Not in Database)';
                missingTitle.style.cssText = 'margin: 0 0 0.5rem; color: #e65100; font-size: 1rem;';
                missingSection.appendChild(missingTitle);

                const missingList = document.createElement('ul');
                missingList.style.cssText = 'margin: 0; padding-left: 1.2rem;';
                data.missing_narrators.forEach(narrator => {
                    const listItem = document.createElement('li');
                    listItem.textContent = narrator;
                    listItem.style.cssText = 'color: #e65100; margin-bottom: 0.25rem;';
                    missingList.appendChild(listItem);
                });
                missingSection.appendChild(missingList);
                narratorsContainer.appendChild(missingSection);
            }

            // Summary
            const summarySection = document.createElement('div');
            summarySection.style.cssText = 'padding: 0.75rem; background-color: #f5f5f5; border-radius: 4px; font-size: 0.9rem; color: #666;';
            const totalNarrators = (data.narrators || []).length;
            const existingCount = (data.existing_narrators || []).length;
            const missingCount = (data.missing_narrators || []).length;
            summarySection.innerHTML = `
                <strong>Summary:</strong> 
                Total narrators found: ${totalNarrators} | 
                Existing in database: ${existingCount} | 
                New/Missing: ${missingCount}
            `;
            narratorsContainer.appendChild(summarySection);

            if (totalNarrators === 0) {
                narratorsContainer.innerHTML = '<p>No narrators found.</p>';
            }

            resultsSection.appendChild(createResultItem(null, narratorsContainer));
        }
    };

    const displayHadithContent = (content) => {
        resultsSection.appendChild(createResultItem(null, content || 'Not available.'));
    };

    const displayKeywordSearchResults = (data) => {
        resultsSection.appendChild(createResultItem(null, `Search Query: <strong>${data.query}</strong> | Total Matches: <strong>${data.total_matches}</strong>`));
        if (data.matched_ayats && data.matched_ayats.length > 0) {
            data.matched_ayats.forEach(ayah => {
                const ayahContent = `
                    <p><strong>Arabic:</strong> ${ayah.arabic_diacritics || ''}</p>
                    <p><strong>English Translation:</strong> ${convertMarkdownHighlights(ayah.english_translation)}</p>
                `;
                resultsSection.appendChild(createResultItem(`Surah ${ayah.surah_name_english} - Ayah ${ayah.aya_number} (Score: ${ayah.score.toFixed(2)})`, ayahContent));
            });
        } else {
            resultsSection.appendChild(createResultItem(null, 'No matching ayats found for your search query.'));
        }
    };

    const displayHighlightedKeywords = (data) => {
        resultsSection.appendChild(createResultItem('Original Text:', `<textarea readonly style="width: 100%; min-height: 100px; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 6px; font-family: inherit; resize: vertical;">${data.original_text}</textarea>`));
        resultsSection.appendChild(createResultItem('Text with Highlighted Keywords:', data.highlighted_text));
        if (data.found_keywords && data.found_keywords.length > 0) {
            const keywordsHtml = data.found_keywords.map(kw => `<span class="keyword">${kw}</span>`).join(' ');
            resultsSection.appendChild(createResultItem('Found Keywords:', keywordsHtml));
        } else {
            resultsSection.appendChild(createResultItem(null, 'No keywords from the database were found in the text.'));
        }
    };
});
