document.addEventListener("DOMContentLoaded", () => {
    const warehouse = document.getElementById("warehouse");

    // Завантаження складу
    fetch("/api/storage-units")
        .then(response => response.json())
        .then(data => {
            renderWarehouse(data);
        })
        .catch(error => console.error("Error loading warehouse:", error));

    // Рендеринг складу
    function renderWarehouse(units) {
        units.forEach(unit => {
            const cell = document.createElement("div");
            cell.classList.add("cell");
            cell.dataset.id = unit.id;
            cell.dataset.row = unit.row;
            cell.dataset.place = unit.place;

            // Встановлення класу за станом
            if (unit.status === "occupied") {
                cell.classList.add("occupied");
            } else if (unit.status === "free") {
                cell.classList.add("free");
            } else if (unit.status === "reserve") {
                cell.classList.add("reserve");
            }

            // Текст на клітинці
            cell.innerText = `${unit.row}-${unit.place}`;
            warehouse.appendChild(cell);

            // Обробка кліку
            cell.addEventListener("click", () => {
                const newStatus = prompt("Enter new status (free, occupied, reserve):");
                if (newStatus) {
                    updateStatus(unit.id, newStatus);
                }
            });
        });
    }

    // Оновлення стану клітинки
    function updateStatus(id, status) {
        fetch(`/api/storage-unit/${id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ status }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert("Status updated!");
                    location.reload(); // Перезавантаження для оновлення
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error updating status:", error));
    }
});
