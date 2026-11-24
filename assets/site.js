/* Evan Promise portfolio — small, dependency-free helpers.
   Everything degrades gracefully: the site is fully readable without JavaScript. */
(function () {
  "use strict";
  var root = document.documentElement;

  /* ---------- Theme toggle (remembered per browser, optional) ---------- */
  function currentTheme() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  var themeBtn = document.querySelector("[data-theme-toggle]");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("ep-theme", next); } catch (e) { /* storage unavailable */ }
    });
  }

  /* ---------- Mobile menu ---------- */
  var menuBtn = document.querySelector("[data-menu-toggle]");
  var nav = document.getElementById("site-nav");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") { nav.classList.remove("open"); menuBtn.setAttribute("aria-expanded", "false"); }
    });
  }

  /* ---------- Project filters ---------- */
  var filterBar = document.querySelector("[data-filters]");
  if (filterBar) {
    var cards = Array.prototype.slice.call(document.querySelectorAll("[data-tags]"));
    var counter = document.querySelector("[data-count]");
    var apply = function (tag) {
      var shown = 0;
      cards.forEach(function (c) {
        var tags = c.getAttribute("data-tags").split("|");
        var ok = tag === "all" || tags.indexOf(tag) > -1;
        c.hidden = !ok;
        if (ok) shown++;
      });
      if (counter) counter.textContent = shown + (shown === 1 ? " project" : " projects");
    };
    filterBar.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-filter]");
      if (!b) return;
      Array.prototype.forEach.call(filterBar.querySelectorAll("button"), function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      apply(b.getAttribute("data-filter"));
    });
    apply("all");
  }

  /* ---------- Table of contents + scroll spy (project pages) ---------- */
  var prose = document.querySelector(".prose");
  var tocList = document.querySelector("[data-toc]");
  if (prose && tocList) {
    var heads = Array.prototype.slice.call(prose.querySelectorAll("h2[id]"));
    heads.forEach(function (h) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = h.textContent;
      li.appendChild(a);
      tocList.appendChild(li);
    });
    if ("IntersectionObserver" in window && heads.length) {
      var links = {};
      Array.prototype.forEach.call(tocList.querySelectorAll("a"), function (a) { links[a.getAttribute("href").slice(1)] = a; });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            Object.keys(links).forEach(function (k) { links[k].classList.remove("active"); });
            if (links[en.target.id]) links[en.target.id].classList.add("active");
          }
        });
      }, { rootMargin: "-90px 0px -65% 0px", threshold: 0 });
      heads.forEach(function (h) { io.observe(h); });
    }
  }

  /* ---------- Image lightbox ---------- */
  var zoomables = document.querySelectorAll(".zoomable img");
  if (zoomables.length) {
    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-label", "Enlarged image");
    box.innerHTML = '<button class="icon-btn" aria-label="Close image" type="button"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button><img alt="">';
    document.body.appendChild(box);
    var big = box.querySelector("img");
    var close = function () { box.classList.remove("open"); };
    Array.prototype.forEach.call(zoomables, function (img) {
      img.setAttribute("tabindex", "0");
      var open = function () { big.src = img.currentSrc || img.src; big.alt = img.alt; box.classList.add("open"); };
      img.addEventListener("click", open);
      img.addEventListener("keydown", function (e) { if (e.key === "Enter") open(); });
    });
    box.addEventListener("click", close);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
  }
})();
