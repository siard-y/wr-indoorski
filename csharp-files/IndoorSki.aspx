<%@ Page Language="C#" AutoEventWireup="true" CodeFile="IndoorSki.aspx.cs" Inherits="Page_IndoorSki" %>

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <title>World Record Indoor Ski</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous" />
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>

    <link rel="stylesheet" href="https://cdn.datatables.net/1.10.25/css/jquery.dataTables.min.css" />
    <script src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js"></script>
    <link rel='stylesheet' href='https://fonts.googleapis.com/css?family=Abel:regular&#038;subset=latin&#038;display=swap' type='text/css' />

    <style>
        body, .bodytext {
            font-size: 1.3em;
            font-family: Abel, Tahoma;
            line-height: 1.6em;
        }

        body {
            background-size: cover;
        }

        .container-fluid {
            max-width: 1024px;
        }

        .jumbotron {
            margin-bottom: 0;
            padding: 1rem 1rem;
        }

        .center {
            margin-left: auto;
            margin-right: auto;
        }

        .trager, .tooLong {
            background-color: red;
            color: white;
        }

        .sneller {
            background-color: green;
            color: white;
        }

        @media only screen and (max-width: 600px) {
            .jumbotron {
                padding: 0.5rem 0.5rem;
                font-weight: bold;
            }

                .jumbotron h1 {
                    font-size: 1.2rem;
                    font-weight: bold;
                }

                .jumbotron h2 {
                    font-size: 1.4rem;
                }

                .jumbotron h3 {
                    font-size: 1.2rem;
                }

            .divTotalen div {
                font-size: 1.2rem;
            }

            .divMetingen div {
                font-size: 1rem;
            }
        }
    </style>
</head>
<body style="margin: 10px auto 10px auto;">
    <form runat="server" id="form1">
        <div class="container-fluid body-content">

            <div class="jumbotron border bg-light">
                <asp:Button ID="btnNieuweMeting" runat="server" Visible="false" CssClass="float-right" OnClick="btnNieuweMeting_Click" Text="NIEUWE METING" OnClientClick="if(!confirm('Zeker?'))return false;" />
                <h2>WR IndoorSki Team S2X</h2>
                <h3>21 en 22 augustus</h3>
                <h3>Huidig record: <%=huidig_record_km.ToString("0.000") %> km</h3>
            </div>
            <br />

            <h1 id="div_header">Waiting voor meting...</h1>
            <div id="divContent">
            </div>
            <br />

            <div class="jumbotron border bg-light">
                <h1>Kijk realtime mee</h1>
                <center>
                    <img src="images/indoorski-qrcode.png" style="max-width: 200px" />
                </center>
            </div>
            <br />
        </div>


        <script>
            function GetData() {
                $.get("./IndoorSki.aspx?jsonTable=1", function (data) {
                    // Set Data
                    if (data != '') {
                        $("#divContent").html(data);
                        $("#span_status").text('Resterend');
                        $("#div_header").html('');
                    }
                });
            }

            var interval1 = setInterval(function () {
                GetData();
            }, 1756);
        </script>

    </form>
</body>
</html>
