// Global variables
let analysisResults = null;

// DOM Elements
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const resultsSection = document.getElementById('resultsSection');
const downloadBtn = document.getElementById('downloadBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Analyze button click
    analyzeBtn.addEventListener('click', handleAnalyze);
    
    // Tab switching
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    // Download button
    downloadBtn.addEventListener('click', downloadReport);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    
    if (file) {
        fileName.textContent = file.name;
        analyzeBtn.disabled = false;
        hideError();
    } else {
        fileName.textContent = 'Choose a file...';
        analyzeBtn.disabled = true;
    }
}

async function handleAnalyze() {
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a file first');
        return;
    }
    
    // Validate file type
    const validExtensions = ['.json', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!validExtensions.includes(fileExtension)) {
        showError('Invalid file type. Please upload a .json or .txt file');
        return;
    }
    
    // Show loading state
    showLoading();
    hideError();
    hideResults();
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Send request to API
        const response = await fetch('/api/analyze/file', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Analysis failed');
        }
        
        // Parse results
        analysisResults = await response.json();
        
        // Display results
        displayResults(analysisResults);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze meeting. Please try again.');
    } finally {
        hideLoading();
    }
}

function displayResults(results) {
    // Display health score
    displayHealthScore(results.health);
    
    // Display summary
    displaySummary(results.summary);
    
    // Display decisions
    displayDecisions(results.decisions);
    
    // Display action items
    displayActionItems(results.action_items);
    
    // Display blockers
    displayBlockers(results.blockers);
    
    // Display processing time
    displayProcessingTime(results.processing_time_seconds);
    
    // Show results section
    showResults();
}

function displayHealthScore(health) {
    const healthScore = document.getElementById('healthScore');
    const healthEmoji = document.getElementById('healthEmoji');
    const healthStatus = document.getElementById('healthStatus');
    
    healthScore.textContent = Math.round(health.score);
    healthEmoji.textContent = health.emoji;
    healthStatus.textContent = health.status.charAt(0).toUpperCase() + health.status.slice(1);
    
    // Remove existing status classes
    healthStatus.classList.remove('healthy', 'at-risk', 'critical');
    
    // Add appropriate class
    if (health.status === 'healthy') {
        healthStatus.classList.add('healthy');
    } else if (health.status === 'at-risk') {
        healthStatus.classList.add('at-risk');
    } else {
        healthStatus.classList.add('critical');
    }
}

function displaySummary(summary) {
    // Executive summary
    document.getElementById('executiveSummary').textContent = summary.executive_summary;
    
    // Key highlights
    const highlightsList = document.getElementById('keyHighlights');
    highlightsList.innerHTML = '';
    summary.key_highlights.forEach(highlight => {
        const li = document.createElement('li');
        li.textContent = highlight;
        highlightsList.appendChild(li);
    });
    
    // Top priorities
    const prioritiesList = document.getElementById('topPriorities');
    prioritiesList.innerHTML = '';
    summary.top_priorities.forEach(priority => {
        const li = document.createElement('li');
        li.textContent = priority;
        prioritiesList.appendChild(li);
    });
    
    // Red flags
    const redFlagsSection = document.getElementById('redFlagsSection');
    const redFlagsList = document.getElementById('redFlags');
    
    if (summary.red_flags && summary.red_flags.length > 0) {
        redFlagsSection.classList.remove('hidden');
        redFlagsList.innerHTML = '';
        summary.red_flags.forEach(flag => {
            const li = document.createElement('li');
            li.textContent = flag;
            redFlagsList.appendChild(li);
        });
    } else {
        redFlagsSection.classList.add('hidden');
    }
    
    // Next steps
    const nextStepsList = document.getElementById('nextSteps');
    nextStepsList.innerHTML = '';
    summary.next_steps.forEach(step => {
        const li = document.createElement('li');
        li.textContent = step;
        nextStepsList.appendChild(li);
    });
}

function displayDecisions(decisions) {
    const decisionsContent = document.getElementById('decisionsContent');
    
    if (!decisions || decisions.length === 0) {
        decisionsContent.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <p>No decisions were identified in this meeting.</p>
            </div>
        `;
        return;
    }
    
    let html = '<h3>Decisions Made</h3>';
    
    decisions.forEach((decision, index) => {
        html += `
            <div class="item-card">
                <h4>Decision ${index + 1}</h4>
                <p><strong>Decision:</strong> ${decision.decision || decision.description || 'N/A'}</p>
                ${decision.decision_maker ? `<p><strong>Decision Maker:</strong> ${decision.decision_maker}</p>` : ''}
                ${decision.rationale ? `<p><strong>Rationale:</strong> ${decision.rationale}</p>` : ''}
                ${decision.confidence ? `<p><strong>Confidence:</strong> ${decision.confidence}</p>` : ''}
            </div>
        `;
    });
    
    decisionsContent.innerHTML = html;
}

function displayActionItems(actionItemsData) {
    const actionsContent = document.getElementById('actionsContent');
    
    const actionItems = actionItemsData.action_items || [];
    
    if (actionItems.length === 0) {
        actionsContent.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">✅</div>
                <p>No action items were identified in this meeting.</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <h3>Action Items (${actionItemsData.total_action_items || actionItems.length})</h3>
        ${actionItemsData.unassigned_tasks > 0 ? 
            `<p style="color: var(--error-red); margin-bottom: 20px;">⚠️ ${actionItemsData.unassigned_tasks} task(s) unassigned</p>` 
            : ''}
        <table class="data-table">
            <thead>
                <tr>
                    <th>Task</th>
                    <th>Owner</th>
                    <th>Deadline</th>
                    <th>Priority</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    actionItems.forEach(item => {
        const priority = item.priority || 'medium';
        html += `
            <tr>
                <td>${item.action || item.task || 'N/A'}</td>
                <td>${item.owner || 'Unassigned'}</td>
                <td>${item.deadline || 'No deadline'}</td>
                <td><span class="priority-badge priority-${priority.toLowerCase()}">${priority}</span></td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    actionsContent.innerHTML = html;
}

function displayBlockers(blockersData) {
    const blockersContent = document.getElementById('blockersContent');
    
    const blockers = blockersData.blockers || [];
    
    if (blockers.length === 0) {
        blockersContent.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">✅</div>
                <p>No blockers were identified in this meeting.</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <h3>Blockers (${blockersData.total_blockers || blockers.length})</h3>
        ${blockersData.critical_blockers > 0 ? 
            `<p style="color: var(--error-red); margin-bottom: 20px;">🔴 ${blockersData.critical_blockers} critical blocker(s)</p>` 
            : ''}
    `;
    
    blockers.forEach((blocker, index) => {
        const severity = blocker.severity || 'medium';
        html += `
            <div class="item-card">
                <h4>Blocker ${index + 1} <span class="severity-badge severity-${severity.toLowerCase()}">${severity}</span></h4>
                <p><strong>Description:</strong> ${blocker.blocker || blocker.description || 'N/A'}</p>
                ${blocker.type ? `<p><strong>Type:</strong> ${blocker.type}</p>` : ''}
                ${blocker.blocking ? `<p><strong>Blocking:</strong> ${blocker.blocking}</p>` : ''}
                ${blocker.owner ? `<p><strong>Owner:</strong> ${blocker.owner}</p>` : ''}
                ${blocker.impact ? `<p><strong>Impact:</strong> ${blocker.impact}</p>` : ''}
            </div>
        `;
    });
    
    blockersContent.innerHTML = html;
}

function displayProcessingTime(seconds) {
    const processingTime = document.getElementById('processingTime');
    processingTime.textContent = `Analysis completed in ${seconds}s`;
}

function switchTab(tabName) {
    // Update tab buttons
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Update tab panes
    const panes = document.querySelectorAll('.tab-pane');
    panes.forEach(pane => {
        if (pane.id === tabName + 'Tab') {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });
}

function downloadReport() {
    if (!analysisResults) {
        showError('No analysis results to download');
        return;
    }
    
    // Generate report text
    const report = generateReportText(analysisResults);
    
    // Create blob and download
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `meeting-analysis-report-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function generateReportText(results) {
    let report = '';
    
    report += '═══════════════════════════════════════════════════════════\n';
    report += '           AI MEETING RESCUE AGENT - ANALYSIS REPORT\n';
    report += '═══════════════════════════════════════════════════════════\n\n';
    
    // Metadata
    if (results.metadata) {
        report += 'MEETING INFORMATION\n';
        report += '─────────────────────────────────────────────────────────\n';
        report += `Title: ${results.metadata.title || 'N/A'}\n`;
        report += `Date: ${results.metadata.date || 'N/A'}\n`;
        report += `Duration: ${results.metadata.duration || 'N/A'}\n`;
        if (results.metadata.participants) {
            report += `Participants: ${results.metadata.participants.join(', ')}\n`;
        }
        report += '\n';
    }
    
    // Health Score
    report += 'MEETING HEALTH SCORE\n';
    report += '─────────────────────────────────────────────────────────\n';
    report += `Score: ${results.health.score}/100 ${results.health.emoji}\n`;
    report += `Status: ${results.health.status.toUpperCase()}\n`;
    report += `Processing Time: ${results.processing_time_seconds}s\n\n`;
    
    // Executive Summary
    report += 'EXECUTIVE SUMMARY\n';
    report += '─────────────────────────────────────────────────────────\n';
    report += `${results.summary.executive_summary}\n\n`;
    
    // Key Highlights
    report += 'KEY HIGHLIGHTS\n';
    report += '─────────────────────────────────────────────────────────\n';
    results.summary.key_highlights.forEach((highlight, i) => {
        report += `${i + 1}. ${highlight}\n`;
    });
    report += '\n';
    
    // Top Priorities
    report += 'TOP PRIORITIES\n';
    report += '─────────────────────────────────────────────────────────\n';
    results.summary.top_priorities.forEach((priority, i) => {
        report += `${i + 1}. ${priority}\n`;
    });
    report += '\n';
    
    // Red Flags
    if (results.summary.red_flags && results.summary.red_flags.length > 0) {
        report += 'RED FLAGS\n';
        report += '─────────────────────────────────────────────────────────\n';
        results.summary.red_flags.forEach((flag, i) => {
            report += `${i + 1}. ${flag}\n`;
        });
        report += '\n';
    }
    
    // Action Items
    const actionItems = results.action_items.action_items || [];
    if (actionItems.length > 0) {
        report += 'ACTION ITEMS\n';
        report += '─────────────────────────────────────────────────────────\n';
        actionItems.forEach((item, i) => {
            report += `${i + 1}. ${item.action || item.task}\n`;
            report += `   Owner: ${item.owner || 'Unassigned'}\n`;
            report += `   Deadline: ${item.deadline || 'No deadline'}\n`;
            report += `   Priority: ${item.priority || 'medium'}\n\n`;
        });
    }
    
    // Blockers
    const blockers = results.blockers.blockers || [];
    if (blockers.length > 0) {
        report += 'BLOCKERS\n';
        report += '─────────────────────────────────────────────────────────\n';
        blockers.forEach((blocker, i) => {
            report += `${i + 1}. [${blocker.severity || 'medium'}] ${blocker.blocker || blocker.description}\n`;
            if (blocker.impact) report += `   Impact: ${blocker.impact}\n`;
            if (blocker.owner) report += `   Owner: ${blocker.owner}\n`;
            report += '\n';
        });
    }
    
    // Recommendations
    if (results.health.recommendations && results.health.recommendations.length > 0) {
        report += 'RECOMMENDATIONS\n';
        report += '─────────────────────────────────────────────────────────\n';
        results.health.recommendations.forEach((rec, i) => {
            report += `${i + 1}. ${rec}\n`;
        });
        report += '\n';
    }
    
    // Next Steps
    report += 'NEXT STEPS\n';
    report += '─────────────────────────────────────────────────────────\n';
    results.summary.next_steps.forEach((step, i) => {
        report += `${i + 1}. ${step}\n`;
    });
    report += '\n';
    
    report += '═══════════════════════════════════════════════════════════\n';
    report += `Generated: ${new Date().toLocaleString()}\n`;
    report += 'Powered by watsonx Orchestrate + Granite LLM\n';
    report += '═══════════════════════════════════════════════════════════\n';
    
    return report;
}

// Utility functions
function showLoading() {
    loadingSpinner.classList.remove('hidden');
}

function hideLoading() {
    loadingSpinner.classList.add('hidden');
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

function showResults() {
    resultsSection.classList.remove('hidden');
}

function hideResults() {
    resultsSection.classList.add('hidden');
}

// Made with Bob
