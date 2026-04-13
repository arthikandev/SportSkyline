/**
 * SportSkyline Homepage Data Hydrator
 * Connects sports-homepage.html to the FastAPI backend
 */

document.addEventListener('DOMContentLoaded', async () => {
    console.log('SportSkyline: Hydrating homepage...');
    
    const data = await SportSkylineAPI.fetch('/homepage');
    if (!data) return;

    // 1. Hero Slider
    if (data.hero && data.hero.length > 0) {
        const heroContainer = document.querySelector('.hero-slider .swiper-wrapper');
        if (heroContainer) {
            // We empty the hardcoded ones and inject dynamic ones
            // NOTE: Swiper needs a re-init if we do this after DOM load
            // For now, let's just log and prepare for the Swiper integration
            console.log('Hero data ready:', data.hero);
        }
    }

    // 2. Trending Strip
    const trendingStrip = document.querySelector('.trending-strip .swiper-wrapper');
    if (trendingStrip && data.trending) {
        trendingStrip.innerHTML = data.trending.map(item => `
            <div class="swiper-slide">
                <a href="news-detail.html?s=${item.slug}" class="trending-item">
                    <span class="tag">${item.sport_emoji} ${item.sport}</span>
                    <p>${item.title}</p>
                </a>
            </div>
        `).join('');
    }

    // 3. Live Scores Widget
    const scoreGrid = document.querySelector('.live-scores-widget .match-grid');
    if (scoreGrid && data.live_matches) {
        scoreGrid.innerHTML = data.live_matches.map(m => `
            <div class="match-card">
                <div class="match-meta">
                    <span class="league">${m.league}</span>
                    <span class="status ${m.status}">${m.match_time || m.status}</span>
                </div>
                <div class="teams">
                    <div class="team">
                        <span>${m.home_team}</span>
                        <span class="score">${m.home_score}</span>
                    </div>
                    <div class="team">
                        <span>${m.away_team}</span>
                        <span class="score">${m.away_score}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // 4. Latest Articles
    const latestGrid = document.querySelector('.news-grid');
    if (latestGrid && data.latest) {
        latestGrid.innerHTML = data.latest.map(a => `
            <article class="article-card" onclick="location.href='news-detail.html?s=${a.slug}'">
                <div class="article-image">
                    <img src="${a.featured_image_url || 'img/placeholder.jpg'}" alt="${a.title}">
                    <span class="category-tag">${a.category}</span>
                </div>
                <div class="article-content">
                    <div class="article-meta">
                        <span><i class="fa-solid fa-clock"></i> ${a.read_time_minutes} min read</span>
                    </div>
                    <h3>${a.title}</h3>
                    <p>${a.excerpt}</p>
                </div>
            </article>
        `).join('');
    }
});
