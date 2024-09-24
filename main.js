const htmlHead = document.querySelector("head");

const htmlBody = document.querySelector("body");

const htmlMain = document.querySelector("main");

const buttonGoTop = createButtonGoTop();

const viewTopics = createViewTopics();

const viewIdiom = createViewIdiom();

const views = [viewTopics, htmlMain, viewIdiom];

const htmlHeader = createHeader();


function getPageName ()
{
	const pagePath = window.location.href;

	if ( pagePath.indexOf( ".html" ) == -1 )
	{
		return "index";
	}

	else
	{
		return pagePath.slice( pagePath.lastIndexOf( "/" ) + 1 , pagePath.indexOf( ".html" ) );
	}
}


function getDirName ()
{
	const pagePath = window.location.href;

	if ( pagePath.indexOf( ".html" ) == -1  && pagePath[pagePath.length - 1] == "/" )
	{
		return pagePath;
	}

	else if ( pagePath.indexOf( ".html" ) == -1  && pagePath[pagePath.length - 1] != "/" )
	{
		return pagePath + "/";
	}

	else
	{
		return pagePath.slice( 0, pagePath.lastIndexOf( "/" ) + 1 );
	}
}


function goTop ()
{
	document.querySelector("header").scrollIntoView();

	return;
}



function createButtonGoTop ()
{
	let buttonGoTop = document.createElement("input");

	buttonGoTop.setAttribute("type", "button");

	buttonGoTop.setAttribute("value", "Top");

	buttonGoTop.setAttribute("id", "goTopButton");

	htmlBody.appendChild(buttonGoTop);

	buttonGoTop.addEventListener("click", goTop);

	return buttonGoTop;
}



function createViewTopics ()
{
	let viewTopics = document.createElement("nav");

	viewTopics.style.display = "none";

	viewTopics.setAttribute( "class", "view" );

	viewTopics.setAttribute( "id", "topics" );

	const headings = document.querySelectorAll("h1");

	for ( let i=0; i < headings.length; i++ )
	{
		headings[i].setAttribute("id", "head" + i);
		
		/* Each anchor is inside a paragraph */
		let section = document.createElement("p");

		let anchor = document.createElement("a");
		
		anchor.setAttribute("href", "#" + headings[i].getAttribute("id"));

		anchor.textContent = headings[i].textContent;

		anchor.addEventListener("click", scrollToHeading);

		section.appendChild(anchor);

		viewTopics.appendChild(section);
	}

	htmlBody.appendChild(viewTopics);

	return viewTopics;
}



function createViewIdiom ()
{
	const idioms = ["pt-BR", "en-US"];

	let viewIdiom = document.createElement("nav");

	viewIdiom.style.display = "none";

	viewIdiom.setAttribute( "id", "idiom");

	let pageName = getPageName();

	let dirName = getDirName();

	console.log(dirName);
	console.log(pageName);

	for ( let i=0; i < idioms.length; i++ )
	{
		pageName = pageName.replace( "." + idioms[i], "" );
	}

	console.log(pageName);

	for ( let i=0; i < idioms.length; i++ )
	{
		let paragraph = document.createElement("p");
		
		if ( idioms[i] == document.querySelector( "meta[lang]" ).getAttribute( "lang" ) )
		{
			let mark = document.createElement("mark");

			mark.textContent = idioms[i];

			paragraph.appendChild(mark);
		}

		else 
		{
			let anchor = document.createElement("a");
		
			anchor.setAttribute("href", dirName + pageName + "." + idioms[i] + ".html");

			anchor.textContent = idioms[i];

			paragraph.appendChild(anchor);
		}

		viewIdiom.appendChild(paragraph);
	}

	htmlBody.appendChild(viewIdiom);

	return viewIdiom;
}


function createHeader ()
{
	const htmlHeader = document.createElement("header");

	htmlBody.insertBefore( htmlHeader, htmlMain );

	const viewSelectors = document.createElement("div");

	viewSelectors.setAttribute("id", "viewSelectors");

	htmlHeader.appendChild(viewSelectors);

	for ( let i = 0; i < views.length; i++)
	{
		let viewSelector = document.createElement("input");

		viewSelector.setAttribute( "type", "button" );

		viewSelector.setAttribute( "class", "viewSelector" );

		if ( views[i].hasAttribute( "id" ) )
		{
			viewSelector.setAttribute( "value", views[i].getAttribute( "id" ) );
		}

		else
		{
			viewSelector.setAttribute( "value", views[i].tagName.toLowerCase() );
		}

		viewSelector.addEventListener( "click", showView );

		viewSelectors.appendChild(viewSelector);
	}

	const title = document.createElement("h1");

	title.textContent = document.querySelector("title").textContent;

	htmlHeader.appendChild(title);

	return htmlHeader;
}


function showView ( event )
{
	for ( let i=0; i < views.length; i++ )
	{
		views[i].style.display = "none";
	}

	let view = document.querySelector( "#" + event.target.getAttribute( "value" ) );

	if ( view == null )
	{
		view = document.querySelector( event.target.getAttribute( "value" ) );
	}

	const viewSelectors = document.querySelectorAll(".viewSelector");

	for ( let i=0; i < viewSelectors.length; i++ )
	{
		viewSelectors[i].style.backgroundColor = "#956800";
	}

	event.target.style.backgroundColor = "#ffcd5b";

	view.style.display = "block";

	return;
}


function showViewByElement ( element )
{
	for ( let i=0; i < views.length; i++ )
	{
		views[i].style.display = "none";
	}

	const viewSelectors = document.querySelectorAll(".viewSelector");

	for ( let i=0; i < viewSelectors.length; i++ )
	{
		if ( viewSelectors[i].getAttribute("value") == element.tagName.toLowerCase() || viewSelectors[i].getAttribute("value") == element.getAttribute( "id" ) )
		{
			viewSelectors[i].style.backgroundColor = "#ffcd5b";
		}

		else
		{
			viewSelectors[i].style.backgroundColor = "#956800";
		}
	}

	element.style.display = "block";

	return;
}


function scrollToHeading ( event )
{
	showViewByElement( htmlMain );

	document.querySelector(event.target.getAttribute("href")).scrollIntoView();

	return;
}



showViewByElement( htmlMain );

