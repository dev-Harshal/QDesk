const createQuestionSetForm = document.getElementById('createQuestionSetForm')
if (createQuestionSetForm) {
    createQuestionSetForm.addEventListener('submit', function(event) {
        event.preventDefault();

        fetch('/teacher/create/question-set/', {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(createQuestionSetForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                popAlert(data)
            }
        })
    })
}

const updateQuestionSetForm = document.getElementById('updateQuestionSetForm')
if (updateQuestionSetForm) {
    updateQuestionSetForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const questionSetId = document.getElementById('questionSetId').value
        
        fetch(`/teacher/update/question-set/${questionSetId}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(updateQuestionSetForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                popAlert(data)
            }
        })

    })
}

const createQuestionForm = document.getElementById('createQuestionForm')
if (createQuestionForm) {
    createQuestionForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const questionSetId = document.getElementById('questionSetId').value

        fetch(`/teacher/create/questions/${questionSetId}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(createQuestionForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                popAlert(data)
            }
        })
    })
}

const updateQuestionForm = document.getElementById('updateQuestionForm')
if (updateQuestionForm) {
    updateQuestionForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const currentUnit = document.getElementById('currentUnit').value
        const subjectId = document.getElementById('subjectId').value;
        
        const url = `/teacher/update/questions/${subjectId}/${currentUnit}/`

        fetch(url, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(updateQuestionForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                popAlert(data)
            }
        })
    })
}

const unitDropdown =  document.getElementById("unit-dropdown")
if (unitDropdown) {
    unitDropdown.addEventListener("change", function() {
        const selectedUnit = this.value;
        const subjectId = document.getElementById('subjectId').value;
        if (selectedUnit) {
            var url = `http://127.0.0.1:8000/teacher/update/questions/${subjectId}/${selectedUnit}/`;
            window.location.href = url;  // Redirect to the URL
        }
    });
}

const questionContainer = document.getElementById('questionContainer');
let questionCount = document.querySelectorAll('.questionRow').length || 0;
const addQuestionRow = document.getElementById('addQuestionRow');

function createQuestionRow(questionCount) {
    const newRow = document.createElement('div');
    newRow.classList.add('row', 'align-items-end', 'mb-3', 'questionRow');
    newRow.setAttribute('data-question-id', questionCount);  // Use a custom data attribute to uniquely identify the row

    newRow.innerHTML =  `
        <div class="col-9">
            <label for="questionTitle" class="form-label">(${questionCount}) Question Title</label>
            <input type="text" class="form-control" id="questionTitle" name="question_title[]" required>
        </div>

        <div class="col-2">
            <label for="questionMark" class="form-label">Question Mark</label>
            <input type="number" class="form-control" id="questionMark" name="question_mark[]" min="1" required>
        </div>

        <div class="col-1">
            <button type="button" value="${questionCount}" class="btn btn-transparent text-end popModal">
                <i class="bi bi-trash3 text-danger" style="cursor: pointer;"></i>
            </button>
        </div>
    `;
    return newRow;
}

function attachRemoveEvent(row) {
    const popModal = row.querySelector('.popModal');
    popModal.addEventListener('click', function(event) {
        const buttonElement = event.currentTarget;
        const questionCount = buttonElement.value;
        openDeleteModal(questionCount);
    });
}

function openDeleteModal(questionCount) {
    const modalBody = document.querySelector('#deleteQuestionModal .modal-body');
    const modalFooterButton = document.querySelector('#deleteQuestionModal .modal-footer .removeRow');

    // Set modal content
    modalBody.innerHTML = `Confirm you want to delete <br> Question (${questionCount}) ?`;
    modalFooterButton.value = questionCount;

    // Clone the button to remove previous event listeners
    const newModalFooterButton = modalFooterButton.cloneNode(true);
    modalFooterButton.replaceWith(newModalFooterButton);

    // Attach a new event listener to delete the correct row
    newModalFooterButton.addEventListener('click', function(event) {
        const questionToDelete = event.currentTarget.value;
        const rowToDelete = document.querySelector(`.questionRow[data-question-id="${questionToDelete}"]`);

        if (rowToDelete) {
            questionContainer.removeChild(rowToDelete);
            updateQuestionNumbers();
        }

        // Close the modal after deleting
        const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteQuestionModal'));
        deleteModal.hide();
    });

    // Show the modal
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteQuestionModal'));
    deleteModal.show();
}

function updateQuestionNumbers() {
    const rows = questionContainer.getElementsByClassName('questionRow');
    for (let i = 0; i < rows.length; i++) {
        const questionLabel = rows[i].querySelector('.form-label');
        const popModalButton = rows[i].querySelector('.popModal');

        questionLabel.innerHTML = `(${i + 1}) Question Title`;
        popModalButton.value = i + 1;
        rows[i].setAttribute('data-question-id', i + 1);  // Update unique identifier
    }
}

// Initialize by attaching event listeners to existing rows
if (questionContainer) {
    const existingRows = questionContainer.getElementsByClassName('questionRow');
    for (let row of existingRows) {
        attachRemoveEvent(row);
    }

    // If no rows exist, create a default row
    if (questionCount === 0) {
        questionCount = 1;
        const newRow = createQuestionRow(questionCount);
        questionContainer.appendChild(newRow);
        attachRemoveEvent(newRow);
    }
}

// Event to add a new question row
if (addQuestionRow) {
    addQuestionRow.addEventListener('click', function(event) {
        questionCount = questionContainer.getElementsByClassName('questionRow').length + 1;
        const newRow = createQuestionRow(questionCount);
        questionContainer.appendChild(newRow);
        attachRemoveEvent(newRow);
    });
}











