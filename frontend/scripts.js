let form = document.getElementById('main-form')
let formdiv = document.getElementById('hider')
let sbtbtn = document.getElementById('submit')
let toshow = document.getElementById('disp')
let body = document.body
function handleForm(event){
    event.preventDefault();
}

form.addEventListener('submit', handleForm);

function butt_click(){
    if(form.elements[0].value && form.elements[1].value && form.elements[2].value && form.elements[3].value && form.elements[4].value && form.elements[5].value ){
        if (18 <= form.elements[1].value && form.elements[1].value <= 110) {
            console.log('sent')
            sbtbtn.value="Processing.."
            axios.post('http://127.0.0.1:8000/getpdfinfo',{
                name:       form.elements[0].value,
                age:        form.elements[1].value,
                fathername: form.elements[5].value,
                gender:     form.elements[2].value,
                state:      form.elements[3].value,
                district:   form.elements[4].value
            }).then((response)=>{
                formdiv.classList.add('initial')
                body.style.backgroundImage = 'none';
                let new_el = document.createElement('textarea')
                let textedJSON =  JSON.stringify(response.data, undefined, 4);
                new_el.value = textedJSON
                toshow.appendChild(new_el)
            }).catch((err)=>{
                console.log(err);
            })
        }
    }

    else{
        alert('please fill all values')
    }
}

sbtbtn.onclick = butt_click










