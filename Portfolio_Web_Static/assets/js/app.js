(() => {
  "use strict";

  const body = document.body;
  const root = document.documentElement;
  const storage = {
    get(key, fallback) {
      try {
        return localStorage.getItem(key) || fallback;
      } catch (_) {
        return fallback;
      }
    },
    set(key, value) {
      try {
        localStorage.setItem(key, value);
      } catch (_) {
        // Preferences remain active for the current page if storage is blocked.
      }
    },
  };

  const browserLanguage = navigator.language?.toLowerCase().startsWith("en") ? "en" : "fr";
  const preferredTheme = window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";

  const state = {
    language: storage.get("portfolio-language", browserLanguage),
    theme: storage.get("portfolio-theme", preferredTheme),
    contrast: storage.get("portfolio-contrast", "normal"),
    text: storage.get("portfolio-text", "normal"),
  };

  const labels = {
    fr: {
      language: "Passer le site en anglais",
      themeLight: "Activer le thème sombre",
      themeDark: "Activer le thème clair",
      contrastOn: "Activer le contraste renforcé",
      contrastOff: "Désactiver le contraste renforcé",
      textOn: "Agrandir le texte",
      textOff: "Rétablir la taille du texte",
      menuOpen: "Ouvrir le menu principal",
      menuClose: "Fermer le menu principal",
      accessOpen: "Ouvrir les réglages d’accessibilité",
      accessClose: "Fermer les réglages d’accessibilité",
    },
    en: {
      language: "Switch the website to French",
      themeLight: "Enable dark theme",
      themeDark: "Enable light theme",
      contrastOn: "Enable enhanced contrast",
      contrastOff: "Disable enhanced contrast",
      textOn: "Increase text size",
      textOff: "Restore text size",
      menuOpen: "Open the main menu",
      menuClose: "Close the main menu",
      accessOpen: "Open accessibility settings",
      accessClose: "Close accessibility settings",
    },
  };

  function setText(selector, value) {
    document.querySelectorAll(selector).forEach((element) => {
      element.textContent = value;
    });
  }

  function applyState() {
    body.dataset.language = state.language;
    body.dataset.theme = state.theme;
    body.dataset.contrast = state.contrast;
    body.dataset.text = state.text;
    root.lang = state.language;
    root.dataset.text = state.text;

    const dictionary = labels[state.language];
    const languageLabel = state.language === "fr" ? "EN" : "FR";
    setText("[data-language-label]", languageLabel);
    document.querySelectorAll("[data-language-toggle]").forEach((button) => {
      button.setAttribute("aria-label", dictionary.language);
    });

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.setAttribute("aria-pressed", String(state.theme === "dark"));
      button.setAttribute("aria-label", state.theme === "dark" ? dictionary.themeDark : dictionary.themeLight);
    });

    document.querySelectorAll("[data-contrast-toggle]").forEach((button) => {
      button.setAttribute("aria-pressed", String(state.contrast === "high"));
      button.setAttribute("aria-label", state.contrast === "high" ? dictionary.contrastOff : dictionary.contrastOn);
    });

    document.querySelectorAll("[data-text-toggle]").forEach((button) => {
      button.setAttribute("aria-pressed", String(state.text === "large"));
      button.setAttribute("aria-label", state.text === "large" ? dictionary.textOff : dictionary.textOn);
    });

    document.querySelectorAll("[data-access-toggle]").forEach((button) => {
      const isOpen = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-label", isOpen ? dictionary.accessClose : dictionary.accessOpen);
    });

    document.title = document.querySelector(`[data-page-title][data-lang="${state.language}"]`)?.textContent || document.title;
    const translatedDescription = document.querySelector(`[data-page-description][data-lang="${state.language}"]`)?.textContent;
    if (translatedDescription) {
      document.querySelector('meta[name="description"]')?.setAttribute("content", translatedDescription);
    }
    document.querySelectorAll("[data-alt-fr][data-alt-en]").forEach((image) => {
      image.setAttribute("alt", image.getAttribute(`data-alt-${state.language}`) || "");
    });
    document.querySelectorAll("[data-aria-fr][data-aria-en]").forEach((element) => {
      element.setAttribute("aria-label", element.getAttribute(`data-aria-${state.language}`) || "");
    });
    document.querySelectorAll("[data-cv-fr][data-cv-en]").forEach((link) => {
      link.setAttribute("href", link.getAttribute(`data-cv-${state.language}`) || "");
    });
    document.querySelectorAll("[data-cv-pdf][data-src-fr][data-src-en]").forEach((embed) => {
      const source = embed.getAttribute(`data-src-${state.language}`) || "";
      if (embed.getAttribute("data") !== source) embed.setAttribute("data", source);
    });
  }

  document.querySelectorAll("[data-language-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      state.language = state.language === "fr" ? "en" : "fr";
      storage.set("portfolio-language", state.language);
      applyState();
    });
  });

  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      state.theme = state.theme === "dark" ? "light" : "dark";
      storage.set("portfolio-theme", state.theme);
      applyState();
    });
  });

  document.querySelectorAll("[data-contrast-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      state.contrast = state.contrast === "high" ? "normal" : "high";
      storage.set("portfolio-contrast", state.contrast);
      applyState();
    });
  });

  document.querySelectorAll("[data-text-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      state.text = state.text === "large" ? "normal" : "large";
      storage.set("portfolio-text", state.text);
      applyState();
    });
  });

  const menuButton = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-main-nav]");
  if (menuButton && navigation) {
    const media = window.matchMedia("(max-width: 62rem)");
    const syncMenu = () => {
      if (media.matches) {
        navigation.hidden = menuButton.getAttribute("aria-expanded") !== "true";
      } else {
        navigation.hidden = false;
        menuButton.setAttribute("aria-expanded", "false");
      }
    };
    menuButton.addEventListener("click", () => {
      const open = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!open));
      navigation.hidden = open;
      menuButton.setAttribute("aria-label", open ? labels[state.language].menuOpen : labels[state.language].menuClose);
    });
    media.addEventListener?.("change", syncMenu);
    syncMenu();
  }

  const accessButton = document.querySelector("[data-access-toggle]");
  const accessPanel = document.querySelector("[data-access-panel]");
  const closeAccess = () => {
    if (!accessButton || !accessPanel) return;
    accessPanel.hidden = true;
    accessButton.setAttribute("aria-expanded", "false");
    accessButton.setAttribute("aria-label", labels[state.language].accessOpen);
  };

  if (accessButton && accessPanel) {
    accessButton.addEventListener("click", () => {
      const willOpen = accessPanel.hidden;
      accessPanel.hidden = !willOpen;
      accessButton.setAttribute("aria-expanded", String(willOpen));
      accessButton.setAttribute("aria-label", willOpen ? labels[state.language].accessClose : labels[state.language].accessOpen);
      if (willOpen) accessPanel.querySelector("button")?.focus();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !accessPanel.hidden) {
        closeAccess();
        accessButton.focus();
      }
    });

    document.addEventListener("click", (event) => {
      if (!accessPanel.hidden && !accessPanel.contains(event.target) && !accessButton.contains(event.target)) {
        closeAccess();
      }
    });
  }

  const projectLinks = [...document.querySelectorAll("[data-project-link]")];
  const caseStudies = [...document.querySelectorAll(".case-study")];
  if (projectLinks.length && caseStudies.length && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;
        projectLinks.forEach((link) => {
          const active = link.getAttribute("href") === `#${visible.target.id}`;
          if (active) link.setAttribute("aria-current", "true");
          else link.removeAttribute("aria-current");
        });
      },
      { rootMargin: "-35% 0px -55%", threshold: [0.05, 0.3, 0.6] },
    );
    caseStudies.forEach((section) => observer.observe(section));
  }

  document.querySelectorAll("[data-current-year]").forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });

  applyState();
})();
