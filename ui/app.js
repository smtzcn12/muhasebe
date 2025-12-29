const toggles = document.querySelectorAll("[data-toggle]");

toggles.forEach((toggle) => {
  toggle.addEventListener("click", () => {
    const targetId = toggle.getAttribute("data-toggle");
    const submenu = document.getElementById(targetId);
    if (!submenu) {
      return;
    }
    submenu.classList.toggle("submenu--open");
  });
});
