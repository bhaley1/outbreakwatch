// Additional JavaScript functions for multi-threat surveillance system
// Add these functions before the closing </script> tag in index.html

// Update AMR alert status
function updateAMRStatus() {
  const banner = document.getElementById('amrAlertBanner');
  const count = document.getElementById('amrAlertCount');
  const summary = document.getElementById('amrAlertSummary');
  
  if (amrThreats.length > 0) {
    banner.classList.add('active');
    count.textContent = `${amrThreats.length} threat${amrThreats.length === 1 ? '' : 's'}`;
    const criticalThreats = amrThreats.filter(t => t.severity_level === 'Critical').length;
    if (criticalThreats > 0) {
      summary.textContent = `${amrThreats.length} AMR threats detected (${criticalThreats} critical)`;
    } else {
      summary.textContent = `${amrThreats.length} antimicrobial resistance threats detected`;
    }
  }
}

// Update vector-borne disease status
function updateVectorStatus() {
  const banner = document.getElementById('vectorAlertBanner');
  const count = document.getElementById('vectorAlertCount');
  const summary = document.getElementById('vectorAlertSummary');
  
  if (vectorOutbreaks.length > 0) {
    banner.classList.add('active');
    count.textContent = `${vectorOutbreaks.length} outbreak${vectorOutbreaks.length === 1 ? '' : 's'}`;
    summary.textContent = `${vectorOutbreaks.length} vector-borne disease outbreak${vectorOutbreaks.length === 1 ? '' : 's'} monitored globally`;
  }
}

// Update HAI status
function updateHAIStatus() {
  const banner = document.getElementById('haiAlertBanner');
  const count = document.getElementById('haiAlertCount');
  const summary = document.getElementById('haiAlertSummary');
  
  if (haiClusters.length > 0) {
    banner.classList.add('active');
    count.textContent = `${haiClusters.length} cluster${haiClusters.length === 1 ? '' : 's'}`;
    summary.textContent = `${haiClusters.length} healthcare-associated infection cluster${haiClusters.length === 1 ? '' : 's'} detected`;
  }
}

// Update VPD status
function updateVPDStatus() {
  const banner = document.getElementById('vpdAlertBanner');
  const count = document.getElementById('vpdAlertCount');
  const summary = document.getElementById('vpdAlertSummary');
  
  if (vpdOutbreaks.length > 0) {
    banner.classList.add('active');
    count.textContent = `${vpdOutbreaks.length} outbreak${vpdOutbreaks.length === 1 ? '' : 's'}`;
    summary.textContent = `${vpdOutbreaks.length} vaccine-preventable disease outbreak${vpdOutbreaks.length === 1 ? '' : 's'} detected`;
  }
}

// Modal functions for AMR
function showAMRModal() {
  const modal = document.getElementById('amrModal');
  const content = document.getElementById('amrContent');
  modal.classList.add('active');
  renderAMRContent(content);
}

function closeAMRModal() {
  const modal = document.getElementById('amrModal');
  modal.classList.remove('active');
}

// Modal functions for Vector-Borne Diseases
function showVectorModal() {
  const modal = document.getElementById('vectorModal');
  const content = document.getElementById('vectorContent');
  modal.classList.add('active');
  renderVectorContent(content);
}

function closeVectorModal() {
  const modal = document.getElementById('vectorModal');
  modal.classList.remove('active');
}

// Modal functions for HAI
function showHAIModal() {
  const modal = document.getElementById('haiModal');
  const content = document.getElementById('haiContent');
  modal.classList.add('active');
  renderHAIContent(content);
}

function closeHAIModal() {
  const modal = document.getElementById('haiModal');
  modal.classList.remove('active');
}

// Modal functions for VPD
function showVPDModal() {
  const modal = document.getElementById('vpdModal');
  const content = document.getElementById('vpdContent');
  modal.classList.add('active');
  renderVPDContent(content);
}

function closeVPDModal() {
  const modal = document.getElementById('vpdModal');
  modal.classList.remove('active');
}

// Click handlers for new modals
document.getElementById('amrModal')?.addEventListener('click', function(e) {
  if (e.target === this) {
    closeAMRModal();
  }
});

document.getElementById('vectorModal')?.addEventListener('click', function(e) {
  if (e.target === this) {
    closeVectorModal();
  }
});

document.getElementById('haiModal')?.addEventListener('click', function(e) {
  if (e.target === this) {
    closeHAIModal();
  }
});

document.getElementById('vpdModal')?.addEventListener('click', function(e) {
  if (e.target === this) {
    closeVPDModal();
  }
});

// Render functions for all surveillance modals
function renderAMRContent(container) {
  if (amrThreats.length === 0) {
    container.innerHTML = '<p style="text-align: center; color: var(--ink-3); padding: 2rem;">No critical AMR threats detected at this time.</p>';
    return;
  }
  
  const sortedThreats = [...amrThreats].sort((a, b) => {
    const severityOrder = { 'Critical': 0, 'High': 1, 'Medium': 2 };
    return severityOrder[a.severity_level] - severityOrder[b.severity_level];
  });
  
  let html = '';
  sortedThreats.forEach(threat => {
    const severityClass = threat.severity_level === 'Critical' ? 'critical' : 'warning';
    const severityIcon = threat.severity_level === 'Critical' ? '🔴' : '🟡';
    
    html += `
      <div class="archive-entry" style="border-left: 4px solid var(--${severityClass});">
        <div class="entry-header">
          <div class="entry-agent">${threat.pathogen}</div>
          <div class="entry-bsl" style="background: var(--${severityClass}-light); color: var(--${severityClass});">
            ${severityIcon} ${threat.severity_level}
          </div>
        </div>
        <div class="entry-details">
          <div class="entry-detail">
            <div class="detail-label">Resistance Mechanism</div>
            <div class="detail-value">${threat.resistance_mechanism}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Location</div>
            <div class="detail-value">${threat.location}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Countries</div>
            <div class="detail-value">${threat.countries.join(', ')}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Isolates/Cases</div>
            <div class="detail-value">${threat.isolates || threat.cases || 'Unknown'}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Mortality Rate</div>
            <div class="detail-value">${threat.mortality_rate ? threat.mortality_rate + '%' : 'Under assessment'}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Source</div>
            <div class="detail-value">${threat.source}</div>
          </div>
        </div>
        <div style="display: flex; gap: 12px; margin-top: 1rem;">
          <a href="https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance" target="_blank" class="entry-link">WHO AMR Information →</a>
        </div>
      </div>
    `;
  });
  
  container.innerHTML = html;
}

function renderVectorContent(container) {
  if (vectorOutbreaks.length === 0) {
    container.innerHTML = '<p style="text-align: center; color: var(--ink-3); padding: 2rem;">No vector-borne disease outbreaks detected at this time.</p>';
    return;
  }
  
  let html = '';
  vectorOutbreaks.forEach(outbreak => {
    const severityClass = outbreak.severity_level === 'High' ? 'critical' : 'warning';
    const severityIcon = outbreak.severity_level === 'High' ? '🔴' : '🟡';
    
    html += `
      <div class="archive-entry" style="border-left: 4px solid var(--${severityClass});">
        <div class="entry-header">
          <div class="entry-agent">${outbreak.disease}</div>
          <div class="entry-bsl" style="background: var(--${severityClass}-light); color: var(--${severityClass});">
            ${severityIcon} ${outbreak.severity_level}
          </div>
        </div>
        <div class="entry-details">
          <div class="entry-detail">
            <div class="detail-label">Vector Species</div>
            <div class="detail-value">${outbreak.vector}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Location</div>
            <div class="detail-value">${outbreak.location}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Countries</div>
            <div class="detail-value">${outbreak.countries.join(', ')}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Cases</div>
            <div class="detail-value">${outbreak.cases.toLocaleString()}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Deaths</div>
            <div class="detail-value">${outbreak.deaths || 'Under investigation'}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Source</div>
            <div class="detail-value">${outbreak.source}</div>
          </div>
        </div>
        <div style="display: flex; gap: 12px; margin-top: 1rem;">
          <a href="https://www.who.int/news-room/fact-sheets/detail/vector-borne-diseases" target="_blank" class="entry-link">WHO Vector Disease Info →</a>
        </div>
      </div>
    `;
  });
  
  container.innerHTML = html;
}

function renderHAIContent(container) {
  if (haiClusters.length === 0) {
    container.innerHTML = '<p style="text-align: center; color: var(--ink-3); padding: 2rem;">No HAI clusters detected at this time.</p>';
    return;
  }
  
  let html = '';
  haiClusters.forEach(cluster => {
    const severityClass = cluster.severity_level === 'Critical' ? 'critical' : 'warning';
    const severityIcon = cluster.severity_level === 'Critical' ? '🔴' : '🟡';
    
    html += `
      <div class="archive-entry" style="border-left: 4px solid var(--${severityClass});">
        <div class="entry-header">
          <div class="entry-agent">${cluster.pathogen}</div>
          <div class="entry-bsl" style="background: var(--${severityClass}-light); color: var(--${severityClass});">
            ${severityIcon} ${cluster.severity_level}
          </div>
        </div>
        <div class="entry-details">
          <div class="entry-detail">
            <div class="detail-label">Infection Type</div>
            <div class="detail-value">${cluster.infection_type}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Facility</div>
            <div class="detail-value">${cluster.facility}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Location</div>
            <div class="detail-value">${cluster.location}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Cases</div>
            <div class="detail-value">${cluster.cases}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Deaths</div>
            <div class="detail-value">${cluster.deaths || 'None reported'}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Source</div>
            <div class="detail-value">${cluster.source}</div>
          </div>
        </div>
        <div style="display: flex; gap: 12px; margin-top: 1rem;">
          <a href="https://www.who.int/news-room/fact-sheets/detail/healthcare-associated-infections" target="_blank" class="entry-link">WHO HAI Information →</a>
        </div>
      </div>
    `;
  });
  
  container.innerHTML = html;
}

function renderVPDContent(container) {
  if (vpdOutbreaks.length === 0) {
    container.innerHTML = '<p style="text-align: center; color: var(--ink-3); padding: 2rem;">No VPD outbreaks detected at this time.</p>';
    return;
  }
  
  let html = '';
  vpdOutbreaks.forEach(outbreak => {
    const severityClass = outbreak.severity_level === 'Critical' ? 'critical' : outbreak.severity_level === 'High' ? 'warning' : 'green';
    const severityIcon = outbreak.severity_level === 'Critical' ? '🔴' : outbreak.severity_level === 'High' ? '🟡' : '🟢';
    
    html += `
      <div class="archive-entry" style="border-left: 4px solid var(--${severityClass});">
        <div class="entry-header">
          <div class="entry-agent">${outbreak.disease}</div>
          <div class="entry-bsl" style="background: var(--${severityClass}-light); color: var(--${severityClass});">
            ${severityIcon} ${outbreak.severity_level}
          </div>
        </div>
        <div class="entry-details">
          <div class="entry-detail">
            <div class="detail-label">Vaccination Status</div>
            <div class="detail-value">${outbreak.vaccination_status}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Location</div>
            <div class="detail-value">${outbreak.location}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Countries</div>
            <div class="detail-value">${outbreak.countries.join(', ')}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Cases</div>
            <div class="detail-value">${outbreak.cases}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Severe Outcomes</div>
            <div class="detail-value">${outbreak.hospitalizations ? outbreak.hospitalizations + ' hospitalizations' : ''}${outbreak.deaths ? (outbreak.hospitalizations ? ', ' : '') + outbreak.deaths + ' deaths' : ''}${outbreak.paralysis_cases ? (outbreak.hospitalizations || outbreak.deaths ? ', ' : '') + outbreak.paralysis_cases + ' paralysis cases' : ''}</div>
          </div>
          <div class="entry-detail">
            <div class="detail-label">Source</div>
            <div class="detail-value">${outbreak.source}</div>
          </div>
        </div>
        <div style="display: flex; gap: 12px; margin-top: 1rem;">
          <a href="https://www.who.int/teams/immunization-vaccines-and-biologicals/diseases" target="_blank" class="entry-link">WHO Immunization Info →</a>
        </div>
      </div>
    `;
  });
  
  container.innerHTML = html;
}
