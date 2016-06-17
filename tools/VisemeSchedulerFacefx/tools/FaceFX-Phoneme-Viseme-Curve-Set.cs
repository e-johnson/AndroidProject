
// this is a standalone program that can be compiled and used
// (hasn't been put into a visual studio project, but that should be trivial)
// this program will take a FaceFX actor file that contains a phoneme -> viseme mapping
// it will generate a curve set that triggers each phoneme in sequence.
// this curve set can be copy/pasted into a .bml file for use in testing.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Xml;

namespace facefx_phoneme_test
{
    class Viseme
    {
        public string viseme;
        public string amount;
    }

    class Program
    {
        static void Main(string[] args)
        {
            Dictionary<string, List<Viseme>> phonemeMap = new Dictionary<string,List<Viseme>>();
            Dictionary<string, List<string>> visemeList = new Dictionary<string, List<string>>();
            visemeList["open"] = new List<string>();
            visemeList["W"] = new List<string>();
            visemeList["ShCh"] = new List<string>();
            visemeList["PBM"] = new List<string>();
            visemeList["FV"] = new List<string>();
            visemeList["wide"] = new List<string>();
            visemeList["tBack"] = new List<string>();
            visemeList["tRoof"] = new List<string>();
            visemeList["tTeeth"] = new List<string>();

            XmlReader xmlReader = XmlReader.Create( @"d:\edwork\gunslinger\tools\facefx-phoneme-test\facefx-phoneme-test\NewActor.xml" );
            while ( xmlReader.Read() )
            {
                // entry line looks like:
                //    <entry phoneme="T" target="open" amount="0.4" />

                if ( xmlReader.NodeType == XmlNodeType.Element &&
                     xmlReader.Name == "entry" )
                {
                    string phoneme = xmlReader.GetAttribute( "phoneme" );
                    string target = xmlReader.GetAttribute( "target" );
                    string amount = xmlReader.GetAttribute( "amount" );

                    Debug.WriteLine(string.Format("{0} - {1} - {2}", phoneme, target, amount));

                    Viseme viseme = new Viseme();
                    viseme.viseme = target;
                    viseme.amount = amount;

                    if (phonemeMap.ContainsKey(phoneme))
                    {
                        phonemeMap[phoneme].Add(viseme);
                    }
                    else
                    {
                        phonemeMap.Add(phoneme, new List<Viseme>());
                        phonemeMap[phoneme].Add(viseme);
                    }
                }


                    /*
                   // if animToProcess hasn't been specified, process all animations in the file
                   if ( animToProcess == "" )
                   {
                      TimingData data = new TimingData();
                      data.name = name;
                      data.outputFile = name + ".bml";
                      ReadXMLFromAnimationAttr( xmlReader, data, remapAnalysisActors );
                      timingData.Add( data );
                   }
                   else if ( animToProcess == name )
                   {
                      TimingData data = new TimingData();
                      data.name = name;
                      data.outputFile = outputFile;
                      ReadXMLFromAnimationAttr( xmlReader, data, remapAnalysisActors );
                      timingData.Add( data );
                      break;
                   }
                     */
            }
            xmlReader.Close();


            // P B T D K G M N NG RA RU FLAP PH F V TH DH S Z SH ZH CX X GH HH R Y L W H TS CH JH IY E EN EH A AA AAN AO AON O ON UW UY EU OE OEN AH IH UU UH AX UX AE ER AXR EXR EY AW AY OY OW

            //       <curve name="W" num_keys="4" owner="user"> 51 0 0 0 51.25 0.700000 0 0 51.75 0.700000 0 0 52 0 0 0  53 0 0 0 53.25 0.500000 0 0 53.75 0.500000 0 0 54 0 0 0  57 0 0 0 57.25 0.850000 0 0 57.75 0.850000 0 0 58 0 0 0  81 0 0 0 81.25 0.550000 0 0 81.75 0.550000 0 0 82 0 0 0  83 0 0 0 83.25 0.550000 0 0 83.75 0.550000 0 0 84 0 0 0  85 0 0 0 85.25 0.550000 0 0 85.75 0.550000 0 0 86 0 0 0  87 0 0 0 87.25 0.550000 0 0 87.75 0.550000 0 0 88 0 0 0  89 0 0 0 89.25 0.550000 0 0 89.75 0.550000 0 0 90 0 0 0  91 0 0 0 91.25 0.850000 0 0 91.75 0.850000 0 0 92 0 0 0  93 0 0 0 93.25 0.550000 0 0 93.75 0.550000 0 0 94 0 0 0  95 0 0 0 95.25 0.550000 0 0 95.75 0.550000 0 0 96 0 0 0  97 0 0 0 97.25 0.550000 0 0 97.75 0.550000 0 0 98 0 0 0  103 0 0 0 103.25 0.550000 0 0 103.75 0.550000 0 0 104 0 0 0  105 0 0 0 105.25 0.550000 0 0 105.75 0.550000 0 0 106 0 0 0  125 0 0 0 125.25 0.550000 0 0 125.75 0.550000 0 0 126 0 0 0  127 0 0 0 127.25 0.550000 0 0 127.75 0.550000 0 0 128 0 0 0  </curve>

            List<string> phonemeList = new List<string>();
            phonemeList.Add("P");
            phonemeList.Add("P");
            phonemeList.Add("B");
            phonemeList.Add("T");
            phonemeList.Add("D");
            phonemeList.Add("K");
            phonemeList.Add("G");
            phonemeList.Add("M");
            phonemeList.Add("N");
            phonemeList.Add("NG");
            phonemeList.Add("RA");
            phonemeList.Add("RU");
            phonemeList.Add("FLAP");
            phonemeList.Add("PH");
            phonemeList.Add("F");
            phonemeList.Add("V");
            phonemeList.Add("TH");
            phonemeList.Add("DH");
            phonemeList.Add("S");
            phonemeList.Add("Z");
            phonemeList.Add("SH");
            phonemeList.Add("ZH");
            phonemeList.Add("CX");
            phonemeList.Add("X");
            phonemeList.Add("GH");
            phonemeList.Add("HH");
            phonemeList.Add("R");
            phonemeList.Add("Y");
            phonemeList.Add("L");
            phonemeList.Add("W");
            phonemeList.Add("H");
            phonemeList.Add("TS");
            phonemeList.Add("CH");
            phonemeList.Add("JH");
            phonemeList.Add("IY");
            phonemeList.Add("E");
            phonemeList.Add("EN");
            phonemeList.Add("EH");
            phonemeList.Add("A");
            phonemeList.Add("AA");
            phonemeList.Add("AAN");
            phonemeList.Add("AO");
            phonemeList.Add("AON");
            phonemeList.Add("O");
            phonemeList.Add("ON");
            phonemeList.Add("UW");
            phonemeList.Add("UY");
            phonemeList.Add("EU");
            phonemeList.Add("OE");
            phonemeList.Add("OEN");
            phonemeList.Add("AH");
            phonemeList.Add("IH");
            phonemeList.Add("UU");
            phonemeList.Add("UH");
            phonemeList.Add("AX");
            phonemeList.Add("UX");
            phonemeList.Add("AE");
            phonemeList.Add("ER");
            phonemeList.Add("AXR");
            phonemeList.Add("EXR");
            phonemeList.Add("EY");
            phonemeList.Add("AW");
            phonemeList.Add("AY");
            phonemeList.Add("OY");
            phonemeList.Add("OW");

            float startTime = 0;
            for (int i = 0; i < phonemeList.Count; i++)
            {
                List<Viseme> list = phonemeMap[phonemeList[i]];
                foreach (Viseme v in list)
                {
                    float time = startTime;
                    visemeList[v.viseme].Add(time.ToString());
                    visemeList[v.viseme].Add("0.0");
                    visemeList[v.viseme].Add("0.0");
                    visemeList[v.viseme].Add("0.0");

                    time += 0.25f;
                    visemeList[v.viseme].Add(time.ToString());
                    visemeList[v.viseme].Add(string.Format("{0:0.00}", Convert.ToDouble(v.amount)));
                    visemeList[v.viseme].Add("0.0");
                    visemeList[v.viseme].Add("0.0");

                    time += 1.50f;
                    visemeList[v.viseme].Add(time.ToString());
                    visemeList[v.viseme].Add(string.Format("{0:0.00}", Convert.ToDouble(v.amount)));
                    visemeList[v.viseme].Add("0.0");
                    visemeList[v.viseme].Add("0.0");

                    time += 0.25f;
                    visemeList[v.viseme].Add(time.ToString());
                    visemeList[v.viseme].Add("0.0");
                    visemeList[v.viseme].Add("0.0");
                    visemeList[v.viseme].Add("0.0");
                }

                foreach (KeyValuePair<string, List<string>> v in visemeList)
                {
                    if (v.Value.Count < ((i + 1) * 16))
                    {
                        float time = startTime;

                        v.Value.Add(time.ToString());
                        v.Value.Add("0.0");
                        v.Value.Add("0.0");
                        v.Value.Add("0.0");

                        time += 0.25f;
                        v.Value.Add(time.ToString());
                        v.Value.Add("0.00");
                        v.Value.Add("0.0");
                        v.Value.Add("0.0");

                        time += 1.50f;
                        v.Value.Add(time.ToString());
                        v.Value.Add("0.00");
                        v.Value.Add("0.0");
                        v.Value.Add("0.0");

                        time += 0.25f;
                        v.Value.Add(time.ToString());
                        v.Value.Add("0.0");
                        v.Value.Add("0.0");
                        v.Value.Add("0.0");
                    }
                }

                startTime += 2;
            }




            foreach (KeyValuePair<string, List<string>> v in visemeList)
            {
                List<string> list = visemeList[v.Key];
                Debug.Write(string.Format(@"       <curve name=""{0}"" num_keys=""{1}"" owner=""user""> ", v.Key, list.Count / 4 ));
                for (int i = 0; i < list.Count; i++)
                {
                    Debug.Write(list[i]);
                    Debug.Write(" ");
                }
                Debug.WriteLine("</curve>");
            }
        }
    }
}
