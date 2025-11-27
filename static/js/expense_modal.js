// static/js/expense_modal.js

(() => {
  const modalEl = document.getElementById("addExpenceModal");
  if (!modalEl) return;

  modalEl.addEventListener("show.bs.modal", (event) => {
    const button = event.relatedTarget;
    const form = modalEl.querySelector("#expenseForm");
    if (!form) return;

    const titleEl = modalEl.querySelector("#expenseModalTitle");
    const badgeEl = modalEl.querySelector("#expenseModalBadge");
    const submitBtn = modalEl.querySelector("#expenseSubmitBtn");
    const amountInput = form.querySelector('input[name="amount"]');
    const dateInput = form.querySelector('input[name="date"]');
    const descInput = form.querySelector('input[name="description"]');
    const categorySelect = form.querySelector('select[name="category"]');

    const defaultAction = form.dataset.defaultAction || form.getAttribute("action");
    const defaultDate =
      form.dataset.defaultDate || new Date().toISOString().slice(0, 10);
    const mode = button?.dataset.mode;

    if (mode === "edit") {
      form.action = button.dataset.action || defaultAction;
      if (amountInput) amountInput.value = button.dataset.amount || "";
      if (dateInput) dateInput.value = button.dataset.date || defaultDate;
      if (descInput) descInput.value = button.dataset.description || "";

      if (categorySelect) {
        const catValue = button.dataset.category || "";
        const optionExists = Array.from(categorySelect.options).some(
          (opt) => opt.value === catValue
        );
        if (catValue && !optionExists) {
          const opt = new Option(catValue, catValue);
          categorySelect.add(opt);
        }
        categorySelect.value = catValue;
      }

      if (titleEl) titleEl.textContent = "Edit Expense";
      if (badgeEl) badgeEl.textContent = "Edit";
      if (submitBtn)
        submitBtn.innerHTML =
          '<i class="bi bi-plus-circle me-1"></i> Update Expense';
    } else {
      form.action = defaultAction;
      form.reset();
      if (dateInput) dateInput.value = defaultDate;
      if (titleEl) titleEl.textContent = "Add Expense";
      if (badgeEl) badgeEl.textContent = "New";
      if (submitBtn)
        submitBtn.innerHTML =
          '<i class="bi bi-plus-circle me-1"></i> Save Expense';
    }
  });
})();
