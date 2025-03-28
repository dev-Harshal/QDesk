const firstName = document.getElementById('firstName')
if (firstName) {
    firstName.addEventListener('keypress', function(e) {
        if (e.key >= '0' && e.key <= '9') {
            e.preventDefault();  
        }
    });
}

const lastName = document.getElementById('lastName')
if (lastName) {
    lastName.addEventListener('keypress', function (e) {
        if (e.key >= '0' && e.key <= '9') {
            e.preventDefault();
        }
    });
}

function popAlert(data) {
    const alertContainer = document.getElementById('alertContainer');
    alertContainer.innerHTML = '';

    let status;
    status = (data.status === 'error') ? 'danger' : 'success'

    let alert = document.createElement('div');
    alert.id = 'alert';
    alert.className = `alert alert-${status}`
    alert.role = 'alert'
    alert.innerHTML = `${data.message}`

    alertContainer.appendChild(alert)
    setTimeout(() => {
        alert.style.display = 'none'
    },3000)
}

alertBox = document.getElementById('alert')
if (alertBox) {
    setTimeout(function() {
        alertBox.style.display = 'none';
    }, 3000);
}

const registerForm = document.getElementById('registerForm')
if (registerForm) {
    registerForm.addEventListener('submit', function(event) {
        event.preventDefault();

        fetch('/register/', {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(registerForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                window.scrollTo({ top: 0, behavior: 'smooth' });
                popAlert(data);
            }
        })
    })
}

const loginForm = document.getElementById('loginForm')
if (loginForm) {
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

        fetch('/login/', {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(loginForm)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.success_url
            }
            else {
                popAlert(data);
            }
        })
    })
}

const membersLoginForm = document.getElementById('membersLoginForm')
if (membersLoginForm) {
    membersLoginForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const role = document.getElementById('role').value

        fetch(`/${role}/login/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(membersLoginForm)
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

const membersProfileForm = document.getElementById('membersProfileForm')
if (membersProfileForm) {
    membersProfileForm.addEventListener('submit', function(event){
        event.preventDefault();

        fetch('/members/update/profile/',{
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body :  new FormData(membersProfileForm)
        }
        )
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

const changePasswordForm = document.getElementById('changePasswordForm')
if (changePasswordForm) {
    changePasswordForm.addEventListener('submit', function(event){
        event.preventDefault();

        fetch('/members/change-password/',{
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body :  new FormData(changePasswordForm)
        }
        )
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


const createHodForm = document.getElementById('createHodForm')
if (createHodForm) {
    createHodForm.addEventListener('submit', function(event) {
        event.preventDefault();

        fetch('/admin/create/hod/', {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(createHodForm)
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

const updateHodForm = document.getElementById('updateHodForm')
if (updateHodForm) {
    updateHodForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const userId = document.getElementById('userId').value

        fetch(`/admin/update/hod/${userId}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(updateHodForm)
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

const createSubjectForm = document.getElementById('createSubjectForm')
if (createSubjectForm) {
    createSubjectForm.addEventListener('submit', function(event) {
        event.preventDefault();

        fetch('/hod/create/subject/', {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(createSubjectForm)
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

const updateSubjectForm = document.getElementById('updateSubjectForm')
if (updateSubjectForm) {
    updateSubjectForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const id = document.getElementById('subjectId').value
        url = 
        
        fetch(`/hod/update/subject/${id}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(updateSubjectForm)
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
        .catch(error => {
            console.error(error)
        })
    })
}

const createTeacherForm = document.getElementById('createTeacherForm')
if (createTeacherForm) {
    createTeacherForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        fetch('/hod/create/teacher/', {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body : new FormData(createTeacherForm)
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

const updateTeacherForm = document.getElementById('updateTeacherForm')
if (updateTeacherForm) {
    updateTeacherForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const userId = document.getElementById('userId').value

        fetch(`/hod/update/teacher/${userId}/`, {
            method : 'POST',
            headers : {
                'X-CSRFToken':document.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body :  new FormData(updateTeacherForm)
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




