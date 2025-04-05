function updateFieldPath() {
    const parentField = document.getElementById('parent_field');
    const selectedOption = parentField.options[parentField.selectedIndex];
    document.getElementById('field_path').value = parentField.value;

    const itemTypes = JSON.parse(document.getElementById('item_types').dataset.types);
    const fieldTypes = JSON.parse(document.getElementById('field_types').dataset.types);

    // Check parent field type
    if (parentField.value) {
        const parentType = selectedOption.getAttribute('data-type');
        const itemType = selectedOption.getAttribute('data-item-type');
        if (parentType === 'list') {
            if (itemType === 'object') {
                const typeSelect = document.getElementById('type');
                typeSelect.disabled = false;
                typeSelect.innerHTML = '';
                itemTypes.forEach(type => {
                    typeSelect.add(new Option(type.label, type.value));
                });
            } else {
                const typeSelect = document.getElementById('type');
                typeSelect.disabled = true;
                typeSelect.value = itemType;
            }
        } else if (parentType !== 'object') {
            const typeSelect = document.getElementById('type');
            typeSelect.disabled = true;
        }
    } else {
        const typeSelect = document.getElementById('type');
        typeSelect.disabled = false;
        typeSelect.innerHTML = '';
        fieldTypes.forEach(type => {
            typeSelect.add(new Option(type.label, type.value));
        });
    }
}

// function deleteField(fieldPath) {
//     if (confirm('確定要刪除這個字段嗎？')) {
//         fetch('{{ url_for("delete_field", filename=filename) }}?field_path=' + fieldPath, {
//             method: 'GET',
//             headers: {
//                 'X-Requested-With': 'XMLHttpRequest'
//             }
//         })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.success) {
//                     // 重新載入頁面以更新字段列表
//                     location.reload();
//                 } else {
//                     alert('刪除失敗：' + data.message);
//                 }
//             })
//             .catch(error => {
//                 console.error('Error:', error);
//                 alert('刪除失敗，請稍後再試');
//             });
//     }
// }


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