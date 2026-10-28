document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("inventory-list");

    tableBody.addEventListener("click", async (event) => {
        const deleteButton = event.target.closest(".js-delete");
        if (!deleteButton) return;

        const itemId = deleteButton.dataset.id;
        if (!confirm(`Delete item ID #${itemId}?`)) return;

        try {
            const response = await fetch(`/items/${itemId}`, {
                method: "DELETE"
            });

            if (response.ok) {
                // One line: refresh the page just like the Add action does
                window.location.reload();
            } else {
                alert("Failed to delete item from server.");
            }
        } catch (error) {
            console.error("Network error during deletion:", error);
        }
    });
});