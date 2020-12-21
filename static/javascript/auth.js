const signupform = document.querySelector('#signupform');
signupform.addEventListener('submit',(e)=>{
  e.preventDefault();
  const email = signupform['signup-email'].value;
  const password = signupform['signup-password'].value;

  auth.createUserWithEmailAndPassword(email,password).then(cred=>{
    window.history.back();
  });
});
