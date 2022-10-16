let form = document.getElementById('main-form')
let sbtbtn = document.getElementById('submit')
let tohide = document.getElementById('open')


function handleForm(event){
    event.preventDefault();
}

form.addEventListener('submit',handleForm);

function butt_click(){

    if(form.elements[0].value && form.elements[1].value && form.elements[2].value && form.elements[3].value && form.elements[4].value && form.elements[5].value ){
        console.log('sent')
        sbtbtn.placeholder='Processing'
        axios.post('http://127.0.0.1:8000/getpdfinfo',{
            name:form.elements[0].value,
            age:form.elements[1].value,
            fathername:form.elements[5].value,
            gender:form.elements[2].value,
            state:form.elements[3].value,
            district:form.elements[4].value
        }).then((response)=>{
            tohide.classList.add('initial')
            let new_el = document.createElement('p')
            new_el.innerText = response.data
            console.log(response)
        }).catch((err)=>{
            console.log(err);
        })
    }

    else{
        alert('please fill all values')
    }
}


sbtbtn.onclick = butt_click










