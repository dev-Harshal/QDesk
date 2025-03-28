const typeSelect = document.getElementById('questionPaperType');

function toggleDateTimeSection() {
    const dateTimeSection = document.getElementById('dateTimeSection');
    const dateField = document.getElementById('examDate');
    const hourField = document.querySelector('input[name="exam_hour"]');

    if (typeSelect.value !== "Assignment") {
        dateTimeSection.style.display = 'block';
        dateField.setAttribute('required', true);
        hourField.setAttribute('required', true);
    } else {
        dateTimeSection.style.display = 'none';
        dateField.removeAttribute('required');
        hourField.removeAttribute('required');
    }
}

if (typeSelect) {
    toggleDateTimeSection();
    typeSelect.addEventListener('change', toggleDateTimeSection);
}

createQuestionPaperForm = document.getElementById('createQuestionPaperForm')
if (createQuestionPaperForm) {
    createQuestionPaperForm.addEventListener('submit', function(event) {
        event.preventDefault();

        fetch('/teacher/create/question-paper/', {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(createQuestionPaperForm)
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

const createDivisionForm = document.getElementById('createDivisionForm')
if (createDivisionForm) {

    createDivisionForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const questionPaperId = document.getElementById('questionPaperId').value

        fetch(`/teacher/create/division/${questionPaperId}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(createDivisionForm)
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


const updateDivisionForm = document.getElementById('updateDivisionForm')
if (updateDivisionForm) {

    updateDivisionForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const questionPaperId = document.getElementById('questionPaperId').value
        const divisionId = document.getElementById('divisionId').value       

        fetch(`/teacher/update/division/${divisionId}/${questionPaperId}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(updateDivisionForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                popAlert(data)
            }
        })
    })
}


const addQuestionsForm = document.getElementById('addQuestionsForm')
if (addQuestionsForm) {

    addQuestionsForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const questionPaperId = document.getElementById('questionPaperId').value
        const divisionId = document.getElementById('divisionId').value

        fetch(`/teacher/add/questions/${divisionId}/${questionPaperId}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(addQuestionsForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                popAlert(data)
            }
        })
    })
}


const updateQuestionListForm = document.getElementById('updateQuestionListForm')
if (updateQuestionListForm) {

    updateQuestionListForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const questionPaperId = document.getElementById('questionPaperId').value
        const divisionId = document.getElementById('divisionId').value

        fetch(`/teacher/update/questions-list/${divisionId}/${questionPaperId}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(updateQuestionListForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                popAlert(data)
            }
        })
    })
}