function doGet(e) {
  var spreadsheetId = '1Gl6AqBOW6sILpQjxjhPhhHq3VK1lZnEOhWtzz1jofS8';
  var res = 0;
  try {
    var action = e.parameter.action;
    var stock = e.parameter.stock;
    var quantity = e.parameter.quantity;
    var rate = e.parameter.rate;
    var balance = e.parameter.balance;

    var sheet = SpreadsheetApp
      .openById(spreadsheetId).getSheetByName("GTNTEX");

    var data = sheet.getDataRange().getValues();


    MailApp.sendEmail({
      to: "vlbhartiya@gmail.com",
      subject: action + ": " + quantity + " of " + stock + " @ " + rate,
      htmlBody: "Current Balance: " + balance
    });


    var d = new Date();
    var timeStamp = d.toLocaleTimeString();

    var rowDate = sheet.appendRow([stock, action, quantity, rate, balance, timeStamp]);
  } catch (ex) {
    res = ex;
  }

  return ContentService.createTextOutput(JSON.stringify(res)).setMimeType(ContentService.MimeType.JSON);
}