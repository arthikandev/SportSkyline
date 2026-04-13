/**
 * SportSkyline Live Scores Data Hydrator
 * Connects live.html to the FastAPI backend
 */

document.addEventListener('DOMContentLoaded', async () => {
    const mainFeed = document.querySelector('.match-feed');
    if (!mainFeed) return;

    async function refreshScores() {
        const data = await SportSkylineAPI.fetch('/live-scores');
        if (!data) return;

        let html = '';

        // Live Matches Section
        if (data.live && data.live.length > 0) {
            html += `<h2 class="feed-title"><span class="live-dot"></span> Live Now</h2>`;
            html += data.live.map(m => renderMatchCard(m, 'live')).join('');
        }

        // Upcoming
        if (data.upcoming && data.upcoming.length > 0) {
            html += `<h2 class="feed-title">Upcoming Fixtures</h2>`;
            html += data.upcoming.map(m => renderMatchCard(m, 'scheduled')).join('');
        }

        mainFeed.innerHTML = html;
    }

    function renderMatchCard(m, type) {
        return `
            <div class="match-card" data-sport="${m.sport_slug}" data-status="${m.status}">
                <div class="match-header">
                    <div class="league-info">
                        <img src="img/leagues/default.png" alt="">
                        <span>${m.sport_emoji} ${m.league} • ${m.round}</span>
                    </div>
                    <div class="match-time ${m.status}">${m.match_time || 'Upcoming'}</div>
                </div>
                <div class="match-main">
                    <div class="team home">
                        <img src="${m.home_team_logo || 'img/teams/default.png'}" alt="">
                        <span class="team-name">${m.home_team}</span>
                    </div>
                    <div class="score-box">
                        <span class="score">${m.home_score} - ${m.away_score}</span>
                    </div>
                    <div class="team away">
                        <span class="team-name">${m.away_team}</span>
                        <img src="${m.away_team_logo || 'img/teams/default.png'}" alt="">
                    </div>
                </div>
                ${m.events_text ? `<div class="match-footer"><p>${m.events_text}</p></div>` : ''}
            </div>
        `;
    }

    refreshScores();
    setInterval(refreshScores, 60000); // Auto-refresh every minute
});
