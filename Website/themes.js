function onThemeSwitch()
{
    console.log('clicked');
    console.log(cssLink.href.substring(cssLink.href.lastIndexOf('/') + 1));
    if(cssLink.href.substring(cssLink.href.lastIndexOf('/') + 1) === "style%20sirius.css")
    {
        cssLink.href = "style dark.css";
        console.log('light theme changed to dark theme');
        localStorage.setItem('theme','dark');
    }
    else
    {
        cssLink.href = "style sirius.css";
        console.log('dark theme changed to sirius theme');
        localStorage.setItem('theme','sirius');
    }
    console.log('switched');
}

const cssLink = document.head.querySelector('link');
const themeSwitch = document.querySelector('#theme-switch');
if (localStorage.getItem('theme')=='dark')
{
    onThemeSwitch();
}
themeSwitch.addEventListener("click", onThemeSwitch);