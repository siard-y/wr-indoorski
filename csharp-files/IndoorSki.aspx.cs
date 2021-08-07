using Newtonsoft.Json;
using System;
using System.Linq;
using System.Globalization;
using System.Threading;
using Digizon.Text;
using Digizon.Data;


public partial class Page_IndoorSki : WebmanagerClassLibrary.Web.UI.PageBase
{
    // VARS
    public string dateTimeFormat = "yyyy-MM-dd HH.mm.ss.fff";
    public double huidig_record_km = 433.459;
    public double omtrek_rol_m = 1.274;
    DateTime meting_start_totaal;


    protected void Page_Load(object sender, EventArgs e)
    {
        // Culture
        CultureInfo ci = new CultureInfo("en-US");
        Thread.CurrentThread.CurrentCulture = ci;
        Thread.CurrentThread.CurrentUICulture = ci;

        // Json
        var settings = new JsonSerializerSettings
        { // 2021-07-23 10.00.33.825548
            DateFormatString = dateTimeFormat,
            DateTimeZoneHandling = DateTimeZoneHandling.Utc
        };

        // Button Show
        btnNieuweMeting.Visible = Security.IsLoggedIn();


        // Meting Start Totaal
        meting_start_totaal = StringFunctions.chkDate(Cache["meting_start_totaal"]);

        // Get Start meting totaal
        if (meting_start_totaal.Year < 2000)
        {
            meting_start_totaal = StringFunctions.chkDate(GenericMySqlFunctions4.ExecuteScalar(ref gi.Database, "SELECT waarde FROM indoorski_settings WHERE naam='meting_start_totaal'", true, 5.0 / 60.0));
            Cache["meting_start_totaal"] = meting_start_totaal;
        }


        // If Pulse Posted
        Pulse new_pulse = null;
        if (Request.InputStream.Length > 20)
        {
            string inputTxt = new System.IO.StreamReader(Request.InputStream).ReadToEnd();
            if (inputTxt != "" && inputTxt.Contains("datum"))
                new_pulse = JsonConvert.DeserializeObject<Pulse>(System.Text.RegularExpressions.Regex.Unescape(inputTxt).Trim('\"'));
        }

        // If JOSN send in URL / FormData
        if (new_pulse != null)
        {
            // Insert in DB
            gi.Database.ExecuteNonQuery(
                @"INSERT INTO `indoorski_pulse` 
                      (`datum`, `datum_previous`, `meting_start`, `counter`, `counter_totaal`, `diff_in_milli_secs`, `snelheid`, `meting_afstand`, `meting_afstand_totaal`, `gem_snelheid`) 
                    VALUES 
                      ( '" + new_pulse.datum + "', " +
                       "'" + new_pulse.datum_previous + "', " +
                       "'" + new_pulse.meting_start + "', "
                           + new_pulse.counter + ", "
                           + new_pulse.counter_totaal + ", "
                           + new_pulse.diff_in_milli_secs + ", "
                           + new_pulse.snelheid + ", "
                           + new_pulse.meting_afstand + ", "
                           + new_pulse.meting_afstand_totaal + ", "
                           + new_pulse.gem_snelheid + ")");

            // Clear Cache
            Cache["jsonTable"] = "";

            // Update Meting Start Totaal
            if (meting_start_totaal.Year < 2000)
            {
                meting_start_totaal = DateTime.Now;
                Cache["meting_start_totaal"] = meting_start_totaal;
                gi.Database.ExecuteNonQuery("UPDATE indoorski_settings SET waarde=" + Functions.MakeDateMySql(meting_start_totaal) + " WHERE naam='meting_start_totaal'");
            }

            // Response
            Visible = false;
            Response.Write("Pulse saved in DB...");
            Response.Flush();
            Response.End();
        }



        // Show JSON only
        if (StringFunctions.chkBool(Request["jsonTable"]))
        {
            // Return html
            var jsonTable = StringFunctions.chkStr(Cache["jsonTable"]);
            var lastUpdate = StringFunctions.chkDate(Cache["lastUpdate"]);


            // debug
            // meting_start_totaal = DateTime.Now.AddDays(-1);


            // Get Data
            if (jsonTable == "" || (DateTime.Now - lastUpdate).TotalSeconds > 1)
            {
                // Clear
                jsonTable = "";

                // Get 5 Last metingen
                var msg = "";
                var list = GenericMySqlFunctions4.GetDataList<Pulse>(ref gi.Database, @"
                    SELECT * 
                    FROM indoorski_pulse
                    WHERE STR_TO_DATE(datum, '%Y-%m-%d %H.%i.%s') BETWEEN " + Functions.MakeDateMySql(meting_start_totaal) + @"
                                                                      AND " + Functions.MakeDateMySql(meting_start_totaal.AddDays(1)) + @"
                      AND snelheid > 0
                      AND meting_afstand > 0
                      AND datum <> meting_start
                    ORDER BY datum DESC LIMIT 5
                ", ref msg, true, 5.0 / 60.0);

                // Check list
                if (list.Count > 0)
                {
                    // Get Pulsen totaal
                    var pulsen_totaal = StringFunctions.chkInt(GenericMySqlFunctions4.ExecuteScalar(ref gi.Database, @"
                        SELECT SUM(pulsen_totaal) pulsen_totaal
                        FROM (
                            SELECT MAX(counter) pulsen_totaal
                            FROM indoorski_pulse
                            WHERE STR_TO_DATE(datum, '%Y-%m-%d %H.%i.%s') BETWEEN " + Functions.MakeDateMySql(meting_start_totaal) + @"
                                                                              AND " + Functions.MakeDateMySql(meting_start_totaal.AddDays(1)) + @"
                            GROUP BY meting_start
                        ) ds1
                    ", true, 5.0 / 60.0));


                    // Calculate
                    var totaal_afstand_meter = omtrek_rol_m * pulsen_totaal;
                    var gem_snelheid_totaal = totaal_afstand_meter / (DateTime.Now - meting_start_totaal).TotalSeconds;
                    var totaal_tijd_eind = meting_start_totaal.AddDays(1) - DateTime.Now;
                    var verwacht_km_24uur = totaal_afstand_meter / (DateTime.Now - meting_start_totaal).TotalSeconds * 60 * 60 * 24 / 1000;

                    // Totalen
                    jsonTable =
                        @"
                        <div class='container-fluid divTotalen'>
                            <div class='row jumbotron border bg-light'>
                                <div class='col-sm-12'><h1>Overzicht</h1></div>
                            </div>
                            <div class='row border bg-light'>
                                <div class='col-5 col-sm-4'><span id='span_status'></status></div> 
                                <div class='col-6 col-sm-4 d-none d-sm-block'>Gestart: " + meting_start_totaal.ToString("HH:mm:ss") + @"</div>            
                                <div class='col-7 col-sm-4'>" + totaal_tijd_eind.Hours.ToString("00") + "u " + totaal_tijd_eind.Minutes.ToString("00") + "m " + totaal_tijd_eind.Seconds.ToString("00") + @"s</div>
                            </div>
                            <div class='row border bg-light'>
                                <div class='col-5 col-sm-4'>Snelheid</div> 
                                <div class='col-6 col-sm-4 d-none d-sm-block'>" + (list.Average(x => x.snelheid)).ToString("0.0") + @" m/s</div>            
                                <div class='col-7 col-sm-4'>" + (list.Average(x => x.snelheid) * 3.6).ToString("0.0") + @" km/u</div>
                            </div>
                            <div class='row border bg-light'>
                                <div class='col-5 col-sm-4'>Gemiddeld</div> 
                                <div class='col-6 col-sm-4 d-none d-sm-block'>" + gem_snelheid_totaal.ToString("0.0") + @" m/s</div>        
                                <div class='col-7 col-sm-4'>" + (gem_snelheid_totaal * 3.6).ToString("0.0") + @" km/u</div>
                            </div>
                            <div class='row border bg-light'>
                                <div class='col-5 col-sm-4'>Totaal</div> 
                                <div class='col-6 col-sm-4 d-none d-sm-block'>" + totaal_afstand_meter.ToString("0") + @" m</div> 
                                <div class='col-7 col-sm-4'>" + (totaal_afstand_meter / 1000).ToString("000.000") + @" km</div>
                            </div>
                            <div class='row border bg-light'>
                                <div class='col-5 col-sm-4'>Verwacht</div> 
                                <div class='col-6 col-sm-4 d-none d-sm-block'>24 uur</div>
                                <div class='col-7 col-sm-4 " + (verwacht_km_24uur > huidig_record_km ? "sneller" : "trager") + "'>" + verwacht_km_24uur.ToString("000.000") + @" km</div>
                            </div>
                        </div>
                        <br>";

                    // Metingen
                    jsonTable += @"
                        <div class='container-fluid divMetingen'>
                            <div class='row jumbotron border bg-light'>
                                <div class='col-sm-12'><h1>Metingen</h1></h1></div>
                            </div>
                            <div class='row border bg-light'>
                                <div class='col-6 col-sm-4'>Moment</div>
                                <div class='col-4 col-sm-4 d-none d-sm-block'>Vorige Puls</div>
                                <div class='col-6 col-sm-4'>Snelheid</div>
                            </div>
                        ";

                    foreach (var puls in list)
                    {
                        var datum = DateTime.ParseExact(puls.datum, "yyyy-MM-dd HH.mm.ss.fff", null);
                        jsonTable += "\r\n <div class='row border bg-light'>";
                        jsonTable += "\r\n     <div class='col-6 col-sm-4'>" + datum.ToString("HH:mm:ss.fff") + "</div>";
                        jsonTable += "\r\n     <div class='col-4 col-sm-4 d-none d-sm-block'>" + puls.diff_in_milli_secs.ToString("0") + " ms</div>";
                        jsonTable += "\r\n     <div class='col-6 col-sm-4'>" + puls.snelheid.ToString("0.00") + " m/s</div>";
                        jsonTable += "\r\n </div>";
                    }

                    jsonTable += @"
                        </div>"; // container

                    // Compress
                    jsonTable = jsonTable.Replace("     ", " ");
                    jsonTable = jsonTable.Replace("    ", " ");
                    jsonTable = jsonTable.Replace("   ", " ");

                } // list not empty
            } // get data

            // Save
            Cache.Insert("jsonTable", jsonTable);
            Cache.Insert("lastUpdate", lastUpdate);

            // Response
            Visible = false;
            Response.Write(jsonTable);
            Response.Flush();
            Response.End();
        }
    }

    protected void btnNieuweMeting_Click(object sender, EventArgs e)
    {
        // Save
        Cache["meting_start_totaal"] = DateTime.MinValue;
        meting_start_totaal = DateTime.MinValue;
        gi.Database.ExecuteNonQuery("UPDATE indoorski_settings SET waarde=NULL WHERE naam='meting_start_totaal'");

        // Reload
        Redirect("~/IndoorSki.aspx");
    }





    public class Pulse
    {
        public double snelheid { get; set; }
        public int counter { get; set; }
        public int counter_totaal { get; set; }
        public string datum_previous { get; set; }
        public double meting_afstand { get; set; }
        public double meting_afstand_totaal { get; set; }
        public double diff_in_milli_secs { get; set; }
        public string meting_start { get; set; }
        public string datum { get; set; }
        public double gem_snelheid { get; set; }
    }





}