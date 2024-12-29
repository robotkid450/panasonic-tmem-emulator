const cam_sel_wrap_div = document.getElementById("cam_sel_holder")


const data = {
    "Cam 1": "1",
    "Cam 2": "2",
    "Cam 3": "3"
}
for (let key in data){
    let label = document.createElement("label");
    label.innerText = key;
    // cam_sel_wrap_div.appendChild(label)
    let radio = document.createElement("input");
    radio.type = "radio";
    radio.name= "cam_sel";
    radio.value = data[key];
    radio.onclick = update_selected_cam
    label.appendChild(radio);
    cam_sel_wrap_div.appendChild(label);

}
function update_selected_cam(){
    console.log("Updating Camera selection")
    let cam_sel_display = document.getElementById("cam_sel_display")
    let cam_selected_list = document.getElementsByName("cam_sel")
    for (i = 0; i <cam_selected_list.length; i++){
        // console.log(cam_selected_list[i])
        if (cam_selected_list[i].checked){
            cam_sel_display.innerText = cam_selected_list[i].value
            console.log("selected cam is: " + cam_selected_list[i].value)
        }
    }

}

async function get_definded_cameras() {
    console.log("get_definded_cameras")
    const resp = await fetch("http://192.168.1.99:8005/api/camera/list", {
        mode: 'no-cors'
        }
    )

    console.log("resp: " + await resp)
    const data = await resp.json()
    return data
}