// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Website — script (script.js)
// Date: 2025-10-04
// ---------------------------------------------------------------------------
const filterButtons = document.querySelectorAll(".filter-button");
const moduleCards = document.querySelectorAll(".module-card");

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;

    filterButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");

    moduleCards.forEach((card) => {
      const isMatch = filter === "all" || card.dataset.category === filter;
      card.classList.toggle("is-hidden", !isMatch);
    });
  });
});
