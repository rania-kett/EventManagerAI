/**
 * landing.js — Animations et interactions page d'accueil premium
 */
(function () {
    "use strict";

    const nav = document.querySelector(".premium-nav");
    const reveals = document.querySelectorAll(".reveal");
    const counters = document.querySelectorAll(".stat-value[data-count]");

    /* Navbar scroll state */
    function onScroll() {
        if (!nav) return;
        nav.classList.toggle("scrolled", window.scrollY > 60);
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    /* Scroll reveal */
    const revealObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    revealObserver.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    reveals.forEach((el) => revealObserver.observe(el));

    /* Animated counters */
    function animateCounter(el) {
        const target = parseInt(el.getAttribute("data-count"), 10);
        const suffix = el.getAttribute("data-suffix") || "";
        const duration = 2000;
        const start = performance.now();

        function format(n) {
            return suffix
                ? n + suffix
                : n.toLocaleString("fr-FR");
        }

        function tick(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = Math.floor(eased * target);
            el.textContent = format(value);
            if (progress < 1) {
                requestAnimationFrame(tick);
            } else {
                el.textContent = format(target);
            }
        }

        requestAnimationFrame(tick);
    }

    const counterObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.4 }
    );

    counters.forEach((el) => counterObserver.observe(el));

    /* Smooth anchor offset for fixed nav */
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", function (e) {
            const id = this.getAttribute("href");
            if (!id || id === "#") return;
            const target = document.querySelector(id);
            if (!target) return;
            e.preventDefault();
            const offset = 90;
            const top =
                target.getBoundingClientRect().top + window.scrollY - offset;
            window.scrollTo({ top, behavior: "smooth" });
        });
    });

    /* Close mobile nav on link click */
    const navCollapse = document.getElementById("premiumNav");
    if (navCollapse) {
        navCollapse.querySelectorAll(".nav-link").forEach((link) => {
            link.addEventListener("click", () => {
                const toggler = document.querySelector(
                    '[data-bs-target="#premiumNav"]'
                );
                if (navCollapse.classList.contains("show") && toggler) {
                    toggler.click();
                }
            });
        });
    }
})();
