function closeParent()
{
    console.log('clicked');
    box.remove();
    console.log('closed');
    localStorage.setItem('noticed','true');
}

//localStorage.setItem('noticed','false');
//closeParent(); // When election is about to begin, remove this line
const cross = document.querySelector('#notice-cross');
const box = document.querySelector('#floating-notice');
//box.querySelector("strong").innerHTML = "We don't respect your privacy";
//box.querySelector("p").innerHTML = "<h4>Like, at all. Now accept my cookies bitch.</h4><h5>Also I cba to make an accept buttons so just click the cross and ignore this.</h5><h6>(There's only 2 cookies, one for saving which theme you set and the other is literally just so you don't see this message again!)</h6>";

if (localStorage.getItem('noticed')=='true')
{
    closeParent();
}
cross.addEventListener("click", closeParent);