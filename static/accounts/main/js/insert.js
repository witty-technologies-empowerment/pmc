var input = document.getElementsByTagName("input");   // Get the first <h1> element in the document
var att = document.createAttribute("class");       // Create a "class" attribute
att.value = "form-control";                           // Set the value of the class attribute
input.setAttributeNode(att);                          // Add the class attribute to <h1>