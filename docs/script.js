document.addEventListener('DOMContentLoaded', function () {
    const navbar = document.querySelector('.navbar');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');

    window.addEventListener('scroll', function () {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    mobileMenuBtn.addEventListener('click', function () {
        navLinks.classList.toggle('active');
        this.classList.toggle('active');
    });

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offsetTop = target.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                navLinks.classList.remove('active');
                mobileMenuBtn.classList.remove('active');
            }
        });
    });

    let lastScrollTop = 0;
    const scrollDirectionElement = document.documentElement;

    function handleScrollAnimation() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const isScrollingDown = scrollTop > lastScrollTop;
        lastScrollTop = scrollTop;

        document.querySelectorAll('.feature-card').forEach((el, i) => {
            const rect = el.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight * 0.85;

            if (isVisible && !isScrollingDown) {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0) scale(1)';
                el.style.filter = 'blur(0)';
            } else if (isVisible && isScrollingDown) {
                const delay = i * 0.1;
                el.style.transitionDelay = `${delay}s`;
                el.style.opacity = '1';
                el.style.transform = 'translateY(0) scale(1)';
                el.style.filter = 'blur(0)';
            } else if (!isVisible && isScrollingDown) {
                el.style.opacity = '0';
                el.style.transform = 'translateY(60px) scale(0.8)';
                el.style.filter = 'blur(4px)';
                el.style.transitionDelay = '0s';
            } else {
                el.style.opacity = '0';
                el.style.transform = 'translateY(40px) scale(0.9)';
                el.style.filter = 'blur(2px)';
                el.style.transitionDelay = '0s';
            }
        });

        document.querySelectorAll('.arch-card').forEach((el, i) => {
            const rect = el.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight * 0.85;

            if (isVisible && !isScrollingDown) {
                el.style.opacity = '1';
                el.style.transform = 'translateX(0) rotate(0deg)';
                el.style.filter = 'blur(0)';
            } else if (isVisible && isScrollingDown) {
                el.style.opacity = '1';
                el.style.transform = 'translateX(0) rotate(0deg)';
                el.style.filter = 'blur(0)';
            } else if (!isVisible && isScrollingDown) {
                el.style.opacity = '0';
                el.style.transform = 'translateX(-50px) rotate(-5deg)';
                el.style.filter = 'blur(4px)';
            } else {
                el.style.opacity = '0';
                el.style.transform = 'translateX(50px) rotate(5deg)';
                el.style.filter = 'blur(2px)';
            }
        });

        document.querySelectorAll('.step').forEach((el, i) => {
            const rect = el.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight * 0.85;

            if (isVisible && !isScrollingDown) {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0) scale(1)';
                el.style.filter = 'blur(0)';
            } else if (isVisible && isScrollingDown) {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0) scale(1)';
                el.style.filter = 'blur(0)';
            } else if (!isVisible && isScrollingDown) {
                el.style.opacity = '0';
                el.style.transform = 'translateY(80px) scale(0.7)';
                el.style.filter = 'blur(6px)';
            } else {
                el.style.opacity = '0';
                el.style.transform = 'translateY(40px) scale(0.8)';
                el.style.filter = 'blur(3px)';
            }
        });

        document.querySelectorAll('.tech-item').forEach((el, i) => {
            const rect = el.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight * 0.85;

            if (isVisible) {
                el.style.opacity = '1';
                el.style.transform = 'scale(1)';
            } else {
                el.style.opacity = '0';
                el.style.transform = 'scale(0.5)';
            }
        });

        const downloadSection = document.querySelector('.download-content');
        if (downloadSection) {
            const rect = downloadSection.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight * 0.8;

            if (isVisible) {
                downloadSection.style.opacity = '1';
                downloadSection.style.transform = 'scale(1) rotate(0deg)';
            } else {
                downloadSection.style.opacity = '0';
                downloadSection.style.transform = 'scale(0.7) rotate(5deg)';
            }
        }

        document.querySelectorAll('.section-header').forEach(el => {
            const rect = el.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight * 0.8;

            if (isVisible && !isScrollingDown) {
                el.querySelector('h2').style.opacity = '1';
                el.querySelector('h2').style.transform = 'translateY(0)';
                el.querySelector('p').style.opacity = '1';
                el.querySelector('p').style.transform = 'translateY(0)';
            } else if (!isVisible) {
                el.querySelector('h2').style.opacity = '0';
                el.querySelector('h2').style.transform = 'translateY(-40px)';
                el.querySelector('p').style.opacity = '0';
                el.querySelector('p').style.transform = 'translateY(30px)';
            }
        });
    }

    window.addEventListener('scroll', handleScrollAnimation, { passive: true });
    handleScrollAnimation();

    const downloadBtn = document.getElementById('downloadBtn');
    const downloadNav = document.getElementById('downloadNav');
    const changelogInfo = document.getElementById('changelog-info');
    const changelogBtn = document.getElementById('btn-changelog');

    async function get_latest_release() {
        const url = "https://api.github.com/repos/Dominiciss/PhonoScribe/releases"

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Response status: ${response.status}`);
            }

            const result = await response.json();

            downloadNav.setAttribute("href", result[0]['assets'][0]['browser_download_url']);
            downloadBtn.setAttribute("href", result[0]['assets'][0]['browser_download_url']);
            downloadBtn.querySelector("span.btn-version").textContent = result[0]['tag_name'];

            changelog = result.map((e) => { return { 'version': e['tag_name'], 'content': e['body'] } });
            changelog.forEach((e) => {
                let div = document.createElement("div");
                changelogInfo.appendChild(div);

                let h6 = document.createElement("h6");
                let p = document.createElement("p");
                h6.innerText = e['version'];
                p.innerText = e['content'];

                div.appendChild(h6)
                div.appendChild(p)
            });

            let totalHeight = 0;

            Array.from(changelogInfo.children).forEach(child => {
                const childBottom = child.offsetTop + child.offsetHeight;
                if (childBottom > totalHeight) {
                    totalHeight = childBottom;
                }
            });

            changelogInfo.querySelector('.changelog-before').style.height = totalHeight + "px";
        } catch (error) {
            console.error(error.message);
        }
    }

    changelogBtn.addEventListener("click", (e) => {
        kbPreview = changelogInfo.parentElement.querySelector(".keyboard-preview")

        if (changelogInfo.classList.contains("hidden")) {
            kbPreview.classList.add("hidden")
            changelogInfo.classList.remove("hidden")
            changelogBtn.textContent = "Go back"
        } else {
            changelogInfo.classList.add("hidden")
            kbPreview.classList.remove("hidden")
            changelogBtn.textContent = "Changelogs"
        }
    })

    if (downloadBtn) {
        get_latest_release();
    }

    const heroElements = document.querySelectorAll('.hero-text > *');
    heroElements.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = `opacity 0.8s ease ${i * 0.2}s, transform 0.8s ease ${i * 0.2}s`;

        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100);
    });

    document.querySelectorAll('.hero-visual').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateX(60px) scale(0.8)';
        el.style.transition = 'opacity 1s ease 0.6s, transform 1s ease 0.6s';

        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateX(0) scale(1)';
        }, 300);
    });

    const style = document.createElement('style');
    style.textContent = `
        .feature-card {
            transition: opacity 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275), 
                        transform 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275),
                        filter 0.6s ease;
        }
        .arch-card {
            transition: opacity 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275), 
                        transform 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275),
                        filter 0.7s ease;
        }
        .step {
            transition: opacity 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275), 
                        transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275),
                        filter 0.5s ease;
        }
        .tech-item {
            transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .download-content {
            transition: opacity 0.8s ease, transform 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .section-header h2, .section-header p {
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
    `;
    document.head.appendChild(style);
});
