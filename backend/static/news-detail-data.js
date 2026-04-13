/**
 * SportSkyline News Detail Hydrator
 * Connects news-detail.html to the FastAPI backend
 */

document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const slug = urlParams.get('s');
    
    if (!slug) {
        console.error('No article slug provided');
        return;
    }

    const article = await SportSkylineAPI.fetch(`/articles/${slug}`);
    if (!article) {
        document.body.innerHTML = '<div class="error-container"><h1>404</h1><p>Article not found</p><a href="index.html">Back to Home</a></div>';
        return;
    }

    // Update DOM
    document.title = `${article.title} | SportSkyline`;
    
    const titleEl = document.querySelector('.article-header h1');
    if (titleEl) titleEl.textContent = article.title;

    const metaEl = document.querySelector('.article-meta');
    if (metaEl) {
        metaEl.innerHTML = `
            <span><i class="fa-solid fa-calendar"></i> ${new Date(article.published_at).toLocaleDateString()}</span>
            <span><i class="fa-solid fa-user"></i> By ${article.author.display_name}</span>
            <span><i class="fa-solid fa-clock"></i> ${article.read_time_minutes} min read</span>
        `;
    }

    const imgEl = document.querySelector('.featured-image img');
    if (imgEl) imgEl.src = article.featured_image_url || 'img/placeholder.jpg';

    const contentEl = document.querySelector('.article-body');
    if (contentEl) {
        contentEl.innerHTML = article.content;
    }

    // Hydrate Related Articles
    const relatedData = await SportSkylineAPI.fetch(`/articles/related/${slug}`);
    const relatedGrid = document.querySelector('.related-news .news-grid');
    if (relatedGrid && relatedData) {
        relatedGrid.innerHTML = relatedData.map(a => `
            <article class="article-card" onclick="location.href='news-detail.html?s=${a.slug}'">
                <div class="article-image">
                    <img src="${a.featured_image_url || 'img/placeholder.jpg'}" alt="${a.title}">
                </div>
                <div class="article-content">
                    <h3>${a.title}</h3>
                </div>
            </article>
        `).join('');
    }
});
