// Keywords Page JavaScript
let allKeywords = {};
let currentFilter = 'all';
let searchQuery = '';

document.addEventListener('DOMContentLoaded', function() {
    console.log('Keywords page DOM loaded');
    initializeKeywordsPage();
    setupEventListeners();
    loadKeywords();
});

function initializeKeywordsPage() {
    console.log('Keywords page initialized');
    showLoading();
}

function setupEventListeners() {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const clearBtn = document.getElementById('clear-search');
    const languageFilter = document.getElementById('language-filter');
    const retryBtn = document.getElementById('retry-btn');
    const exportBtn = document.getElementById('export-btn');
    const printBtn = document.getElementById('print-btn');

    // Search functionality
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    searchBtn.addEventListener('click', handleSearch);
    clearBtn.addEventListener('click', clearSearch);
    languageFilter.addEventListener('change', handleFilterChange);
    retryBtn.addEventListener('click', loadKeywords);
    exportBtn.addEventListener('click', exportKeywords);
    printBtn.addEventListener('click', printKeywords);
}

async function loadKeywords() {
    try {
        showLoading();
        hideError();
        
        console.log('Attempting to fetch keywords from /api/keywords');
        const response = await fetch('/api/keywords');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        allKeywords = await response.json();
        console.log('Loaded keywords:', allKeywords);
        
        // Validate data structure
        if (!allKeywords.english || !allKeywords.arabic || !allKeywords.urdu) {
            console.error('Invalid data structure:', allKeywords);
            throw new Error('Invalid keywords data structure');
        }
        
        console.log('Keywords loaded successfully:', {
            english: allKeywords.english.length,
            arabic: allKeywords.arabic.length, 
            urdu: allKeywords.urdu.length
        });
        
        updateStats();
        displayKeywords();
        hideLoading();
        
    } catch (error) {
        console.error('Error loading keywords:', error);
        showError();
        hideLoading();
    }
}

function displayKeywords() {
    const filteredKeywords = getFilteredKeywords();
    
    // Clear existing content
    clearKeywordLists();
    
    const rowsContainer = document.getElementById('keywords-rows');
    if (!rowsContainer) return;
    
    rowsContainer.innerHTML = '';
    
    // If we have a search query, we need to handle row creation differently
    if (searchQuery) {
        const searchLower = searchQuery.toLowerCase();
        const matchingRows = [];
        
        // Find all matching rows
        const maxLength = Math.max(
            allKeywords.english ? allKeywords.english.length : 0,
            allKeywords.arabic ? allKeywords.arabic.length : 0,
            allKeywords.urdu ? allKeywords.urdu.length : 0
        );
        
        for (let i = 0; i < maxLength; i++) {
            const englishKeyword = allKeywords.english[i] || '';
            const arabicKeyword = allKeywords.arabic[i] || '';
            const urduKeyword = allKeywords.urdu[i] || '';
            
            const englishMatch = englishKeyword.toLowerCase().includes(searchLower);
            const arabicMatch = arabicKeyword.toLowerCase().includes(searchLower);
            const urduMatch = urduKeyword.toLowerCase().includes(searchLower);
            
            if (englishMatch || arabicMatch || urduMatch) {
                matchingRows.push({
                    index: i + 1,
                    english: englishKeyword,
                    arabic: arabicKeyword,
                    urdu: urduKeyword
                });
            }
        }
        
        // Create rows for matching results
        matchingRows.forEach((rowData, displayIndex) => {
            createKeywordRow(rowData, displayIndex);
        });
        
        // Update counts
        updateColumnCount('english', matchingRows.length);
        updateColumnCount('arabic', matchingRows.length);
        updateColumnCount('urdu', matchingRows.length);
        
    } else {
        // No search - display all or filtered by language
        const maxLength = Math.max(
            filteredKeywords.english ? filteredKeywords.english.length : 0,
            filteredKeywords.arabic ? filteredKeywords.arabic.length : 0,
            filteredKeywords.urdu ? filteredKeywords.urdu.length : 0
        );
        
        for (let i = 0; i < maxLength; i++) {
            const rowData = {
                index: i + 1,
                english: filteredKeywords.english && i < filteredKeywords.english.length ? filteredKeywords.english[i] : '',
                arabic: filteredKeywords.arabic && i < filteredKeywords.arabic.length ? filteredKeywords.arabic[i] : '',
                urdu: filteredKeywords.urdu && i < filteredKeywords.urdu.length ? filteredKeywords.urdu[i] : ''
            };
            
            createKeywordRow(rowData, i);
        }
        
        // Update column counts
        updateColumnCount('english', filteredKeywords.english ? filteredKeywords.english.length : 0);
        updateColumnCount('arabic', filteredKeywords.arabic ? filteredKeywords.arabic.length : 0);
        updateColumnCount('urdu', filteredKeywords.urdu ? filteredKeywords.urdu.length : 0);
    }
    
    updateVisibleCount();
    showKeywordsGrid();
}

function createKeywordRow(rowData, displayIndex) {
    const rowsContainer = document.getElementById('keywords-rows');
    const row = document.createElement('div');
    row.className = 'keyword-row';

    // Helper to process and format keywords
    const processAndFormatKeyword = (keyword) => {
        if (!keyword) return '';
        
        // First, handle comma-separated values
        let parts = keyword.split(',').map(k => k.trim());
        
        // Now, fix concatenated words within each part
        let correctedParts = parts.map(part => {
            // Insert a space before any capital letter that is preceded by a lowercase letter (camelCase)
            let spacedPart = part.replace(/([a-z])([A-Z])/g, '$1 $2');
            
            // Specifically handle the "make..." issue if it's still not spaced
            if (spacedPart.startsWith('make') && spacedPart.length > 4 && !spacedPart.includes(' ')) {
                spacedPart = 'make ' + spacedPart.substring(4);
            }
            
            return spacedPart;
        });

        return correctedParts.join(', ');
    };

    // English cell
    const englishCell = document.createElement('div');
    englishCell.className = 'keyword-cell english-cell';
    if (rowData.english) {
        const formattedKeyword = processAndFormatKeyword(rowData.english);
        const displayText = highlightSearchTerm(formattedKeyword, searchQuery);
        englishCell.innerHTML = `<span class="keyword-index">${rowData.index}.</span> ${displayText}`;
    }
    
    // Arabic cell
    const arabicCell = document.createElement('div');
    arabicCell.className = 'keyword-cell arabic-cell';
    if (rowData.arabic) {
        const formattedKeyword = processAndFormatKeyword(rowData.arabic);
        const displayText = highlightSearchTerm(formattedKeyword, searchQuery);
        arabicCell.innerHTML = displayText;
    }
    
    // Urdu cell
    const urduCell = document.createElement('div');
    urduCell.className = 'keyword-cell urdu-cell';
    if (rowData.urdu) {
        const formattedKeyword = processAndFormatKeyword(rowData.urdu);
        const displayText = highlightSearchTerm(formattedKeyword, searchQuery);
        urduCell.innerHTML = displayText;
    }
    
    // Add click events
    [englishCell, arabicCell, urduCell].forEach((cell, langIndex) => {
        cell.addEventListener('click', function() {
            const languages = ['english', 'arabic', 'urdu'];
            const keywords = [rowData.english, rowData.arabic, rowData.urdu];
            selectKeyword(keywords[langIndex], languages[langIndex], rowData.index);
        });
    });
    
    row.appendChild(englishCell);
    row.appendChild(arabicCell);
    row.appendChild(urduCell);
    rowsContainer.appendChild(row);
}

function clearKeywordLists() {
    const rowsContainer = document.getElementById('keywords-rows');
    if (rowsContainer) {
        rowsContainer.innerHTML = '';
    }
}

function getFilteredKeywords() {
    let filtered = {};
    
    // Apply language filter
    if (currentFilter === 'all') {
        filtered = { ...allKeywords };
    } else {
        filtered[currentFilter] = allKeywords[currentFilter] || [];
    }
    
    // Apply search filter - search across all languages but keep row alignment
    if (searchQuery) {
        const searchLower = searchQuery.toLowerCase();
        const matchingIndices = new Set();
        
        // Find all indices where any language matches the search term
        const maxLength = Math.max(
            allKeywords.english ? allKeywords.english.length : 0,
            allKeywords.arabic ? allKeywords.arabic.length : 0,
            allKeywords.urdu ? allKeywords.urdu.length : 0
        );
        
        for (let i = 0; i < maxLength; i++) {
            const englishMatch = allKeywords.english[i] && 
                allKeywords.english[i].toLowerCase().includes(searchLower);
            const arabicMatch = allKeywords.arabic[i] && 
                allKeywords.arabic[i].toLowerCase().includes(searchLower);
            const urduMatch = allKeywords.urdu[i] && 
                allKeywords.urdu[i].toLowerCase().includes(searchLower);
            
            if (englishMatch || arabicMatch || urduMatch) {
                matchingIndices.add(i);
            }
        }
        
        // Filter all languages based on matching indices
        Object.keys(filtered).forEach(language => {
            if (allKeywords[language]) {
                filtered[language] = Array.from(matchingIndices)
                    .map(index => allKeywords[language][index])
                    .filter(keyword => keyword !== undefined);
            }
        });
    }
    
    return filtered;
}function highlightSearchTerm(text, searchTerm) {
    if (!searchTerm) return text;
    
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

function handleSearch() {
    const searchInput = document.getElementById('search-input');
    searchQuery = searchInput.value.trim();
    displayKeywords();
}

function clearSearch() {
    const searchInput = document.getElementById('search-input');
    searchInput.value = '';
    searchQuery = '';
    currentFilter = 'all';
    document.getElementById('language-filter').value = 'all';
    displayKeywords();
}

function handleFilterChange() {
    const filter = document.getElementById('language-filter').value;
    currentFilter = filter;
    displayKeywords();
}

function selectKeyword(keyword, language, index) {
    // Find corresponding keywords in other languages
    const correspondingKeywords = {
        english: allKeywords.english[index],
        arabic: allKeywords.arabic[index],
        urdu: allKeywords.urdu[index]
    };
    
    // Highlight all corresponding keywords
    highlightCorrespondingKeywords(index);
    
    // Show info (you can expand this)
    console.log('Selected keyword:', correspondingKeywords);
    
    // Optional: Show a tooltip or modal with all translations
    showKeywordDetails(correspondingKeywords, index);
}

function highlightCorrespondingKeywords(index) {
    // Remove previous highlights
    document.querySelectorAll('.keyword-item.highlighted').forEach(item => {
        item.classList.remove('highlighted');
    });
    
    // Highlight corresponding items
    ['english', 'arabic', 'urdu'].forEach(language => {
        const container = document.getElementById(`${language}-keywords`);
        const item = container.querySelector(`[data-index="${index}"]`);
        if (item) {
            item.classList.add('highlighted');
        }
    });
}

function showKeywordDetails(keywords, index) {
    // Create a simple tooltip or use console for now
    const detail = `
        Index: ${index + 1}
        English: ${keywords.english}
        Arabic: ${keywords.arabic}
        Urdu: ${keywords.urdu}
    `;
    
    // You can replace this with a modal or tooltip
    console.log(detail);
    
    // Optional: Show as a temporary notification
    showNotification(`${keywords.english} | ${keywords.arabic} | ${keywords.urdu}`);
}

function showNotification(message) {
    // Create temporary notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #333;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 1000;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

function updateStats() {
    const totalCount = allKeywords.english ? allKeywords.english.length : 0;
    
    document.getElementById('total-keywords').textContent = totalCount;
    document.getElementById('english-count').textContent = allKeywords.english ? allKeywords.english.length : 0;
    document.getElementById('arabic-count').textContent = allKeywords.arabic ? allKeywords.arabic.length : 0;
    document.getElementById('urdu-count').textContent = allKeywords.urdu ? allKeywords.urdu.length : 0;
}

function updateColumnCount(language, count) {
    const countElement = document.getElementById(`${language}-visible`);
    if (countElement) {
        countElement.textContent = count;
    }
}

function updateVisibleCount() {
    const filtered = getFilteredKeywords();
    const totalVisible = Object.values(filtered).reduce((sum, keywords) => sum + keywords.length, 0);
    document.getElementById('visible-count').textContent = totalVisible;
}

function showLoading() {
    document.getElementById('loading-spinner').style.display = 'block';
    document.getElementById('keywords-grid').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading-spinner').style.display = 'none';
}

function showKeywordsGrid() {
    document.getElementById('keywords-grid').style.display = 'grid';
}

function showError() {
    document.getElementById('error-message').style.display = 'block';
    document.getElementById('keywords-grid').style.display = 'none';
}

function hideError() {
    document.getElementById('error-message').style.display = 'none';
}

function exportKeywords() {
    try {
        const dataToExport = {
            metadata: {
                exportDate: new Date().toISOString(),
                totalKeywords: allKeywords.english ? allKeywords.english.length : 0,
                languages: ['english', 'arabic', 'urdu']
            },
            keywords: allKeywords
        };
        
        const dataStr = JSON.stringify(dataToExport, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `islamic-keywords-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        showNotification('Keywords exported successfully!');
    } catch (error) {
        console.error('Export failed:', error);
        showNotification('Export failed. Please try again.');
    }
}

function printKeywords() {
    window.print();
}

// Utility function for debouncing search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('search-input').focus();
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        clearSearch();
    }
});

// Auto-refresh keywords every 5 minutes (optional)
setInterval(function() {
    if (document.visibilityState === 'visible') {
        loadKeywords();
    }
}, 300000);
