
function showAddFieldForm(key) {
    document.getElementById('field_path').value = key;
    document.getElementById('addFieldForm').style.display = 'block';
}

function toggleItemType() {
    const typeSelect = document.getElementById('type');
    const itemTypeRow = document.getElementById('item_type_row');
    itemTypeRow.style.display = typeSelect.value === 'list' ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    toggleItemType();
    updateFieldPath();
});