
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Xml;
using System.Xml.Schema;


namespace VisemeSchedulerFacefx
{
   class Program
   {
      public class PhonemeData
      {
         public string phoneme;
         public double start;
         public double end;

         public string visemeMatch;

         public PhonemeData( string phoneme, double start, double end ) { this.phoneme = phoneme; this.start = start; this.end = end; visemeMatch = ""; }
      }


      public class WordBreakData
      {
         public string word;
         public double start;
         public double end;

         public WordBreakData( string word, double start, double end ) { this.word = word; this.start = start; this.end = end; }
      }


      public class CurveData : IComparable<CurveData>
      {
         public string name;
         public double startTime;
         public double endTime;
         public double value;
         public double slopeIn;
         public double slopeOut;

         public bool endTimeSet;

         public CurveData( string name, double startTime, double value, double slopeIn, double slopeOut ) { this.name = name; this.startTime = startTime; this.endTime = 0; this.value = value; this.slopeIn = slopeIn; this.slopeOut = slopeOut; this.endTimeSet = false; }

         public int CompareTo( CurveData other ) { return startTime.CompareTo( other.startTime ); }
      }

      public class FaceFXCurveDataXML
      {
         public string name;
         public int numKeys;
         public string owner;
         public string curveData;

         public FaceFXCurveDataXML( string name, int numKeys, string owner, string curveData ) { this.name = name; this.numKeys = numKeys; this.owner = owner; this.curveData = curveData; }
      }


      public class TimingData
      {
         public string name;
         public string outputFile;
         public List<PhonemeData> phonemeData;
         public List<WordBreakData> wordBreakData;
         public List<CurveData> curveData;
         public List<FaceFXCurveDataXML> facefxCurveDataXML;
      }


      static void Main( string [] args )
      {
         string inputFile;
         string animToProcess = "";
         string outputFile;
         bool   remapAnalysisActors = false;
         string mapping = "sbm2";

         if ( args.Length < 1 )
         {
            Console.WriteLine();
            Console.WriteLine( "usage:  VisemeSchedulerFacefx [-mapping sbm|sbm2] [-remap] <facefx .xml file> [<animation to process>] [<smartbody .bml.txt file>]" );
            Console.WriteLine( "        -remap will map 'Analysis Actor' names to action units (where possible)" );
            Console.WriteLine( "        -mapping will use the sbm mapping or the sbm2 mapping" );
            Console.WriteLine( "        for <lips> section only.  Doesn't affect the <curves> section.  Can be:" );
            Console.WriteLine( "           -mapping sbm" );
            Console.WriteLine( "           -mapping sbm2" );
            Console.WriteLine( "           defaults is sbm2");
            return;

            //inputFile = @"example.xml";
            //animToProcess = @"line2";
         }

         int argIndex = 0;

         if (args[argIndex] == "-mapping")
         {
             if ( args.Length >= argIndex + 1 + 1 )
             {
                mapping = args[argIndex + 1];
                argIndex += 2;
             }
         }

         if (args[argIndex] == "-remap")
         {
            remapAnalysisActors = true;
            argIndex++;
         }


         if ( args.Length <= argIndex + 1 )
         {
            inputFile = args[ argIndex ];
         }
         else
         {
            inputFile = args[ argIndex ];
            animToProcess = args[ argIndex + 1 ];
         }

         if ( args.Length >= argIndex + 3 )
         {
            outputFile = args[ argIndex + 2 ];
         }
         else
         {
            outputFile = animToProcess + ".bml.txt";
         }


         List<TimingData> timingData = new List<TimingData>();

         XmlReader xmlReader = XmlReader.Create( inputFile );
         while ( xmlReader.Read() )
         {
            // animation line looks like:
            //    <animation name="line2" language="USEnglish" analysis_actor="Default" audio_path="D:\simcoach\simcoachart\scenes\character\ChrMale001\FaceFxFiles\Audio\line2.wav" audio_path_full="D:\simcoach\simcoachart\scenes\character\ChrMale001\FaceFxFiles\Audio\line2.wav">

            if ( xmlReader.NodeType == XmlNodeType.Element &&
                 xmlReader.Name == "animation" )
            {
               string name = xmlReader.GetAttribute( "name" );

               // if animToProcess hasn't been specified, process all animations in the file
               if ( animToProcess == "" )
               {
                  TimingData data = new TimingData();
                  data.name = name;
                  data.outputFile = name + ".bml.txt";
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
            }
         }
         xmlReader.Close();


         foreach ( TimingData d in timingData )
         {
            //                             0                             5                             10                            15                          20                           25                          30                            35                            40
            // string [] phonemeIndex = { "Iy", "Ih", "Eh", "Ey", "Ae", "Aa", "Aw", "Ay", "Ah", "Ao", "Oy", "Ow", "Uh", "Uw", "Er", "Ax", "S", "Sh", "Z", "Zh", "F", "Th", "V", "Dh", "M",   "N",  "Ng", "L", "R", "W",  "Y",  "Hh", "B",   "D", "Jh", "G",  "P",   "T", "K",  "Ch", "Sil", "ShortSil", "Flap" };    // Impersonator
            //string [] phonemeToViseme = { "EE", "Ih", "Ih", "Ih", "Ih", "Ao", "Ih", "Ih", "Ih", "Ao", "oh", "oh", "oh", "oh", "Er", "Ih", "Z", "j",  "Z", "j",  "F", "Th", "F", "Th", "BMP", "NG", "NG", "D", "R", "OO", "OO", "Ih", "BMP", "D", "j",  "KG", "BMP", "D", "KG", "j",  "_",   "_",        "_" };

            Dictionary< string, string > phonemeToVisemeMap = new Dictionary<string,string>();

            // taken from the SBM column in facefx-phoneme-to-viseme-map.xls
            if (mapping == "sbm")
            {
            phonemeToVisemeMap.Add( "P",  "BMP" );
            phonemeToVisemeMap.Add( "B",  "BMP" );
            phonemeToVisemeMap.Add( "T",  "D" );
            phonemeToVisemeMap.Add( "D",  "D" );
            phonemeToVisemeMap.Add( "K",  "KG" );
            phonemeToVisemeMap.Add( "G",  "KG" );
            phonemeToVisemeMap.Add( "M",  "BMP" );
            phonemeToVisemeMap.Add( "N",  "NG" );
            phonemeToVisemeMap.Add( "NG", "NG" );
            phonemeToVisemeMap.Add( "RA", "Er" );
            phonemeToVisemeMap.Add( "RU", "Er" );
            phonemeToVisemeMap.Add( "FLAP", "D" );
            phonemeToVisemeMap.Add( "PH", "F" );
            phonemeToVisemeMap.Add( "F",  "F" );
            phonemeToVisemeMap.Add( "V",  "F" );
            phonemeToVisemeMap.Add( "TH", "Th" );
            phonemeToVisemeMap.Add( "DH", "Th" );
            phonemeToVisemeMap.Add( "S",  "Z" );
            phonemeToVisemeMap.Add( "Z",  "Z" );
            phonemeToVisemeMap.Add( "SH", "j" );
            phonemeToVisemeMap.Add( "ZH", "j" );
            phonemeToVisemeMap.Add( "CX", "Ih" );
            phonemeToVisemeMap.Add( "X",  "Ih" );
            phonemeToVisemeMap.Add( "GH", "KG" );
            phonemeToVisemeMap.Add( "HH", "Ih" );
            phonemeToVisemeMap.Add( "R",  "R" );
            phonemeToVisemeMap.Add( "Y",  "OO" );
            phonemeToVisemeMap.Add( "L",  "Th" );
            phonemeToVisemeMap.Add( "W",  "Ao" );
            phonemeToVisemeMap.Add( "H",  "oh" );
            phonemeToVisemeMap.Add( "TS", "D" );
            phonemeToVisemeMap.Add( "CH", "KG" );
            phonemeToVisemeMap.Add( "JH", "KG" );

            phonemeToVisemeMap.Add( "IY", "EE" );
            phonemeToVisemeMap.Add( "E",  "Ih" );
            phonemeToVisemeMap.Add( "EN", "Ih" );
            phonemeToVisemeMap.Add( "EH", "Ih" );
            phonemeToVisemeMap.Add( "A",  "Ao" );
            phonemeToVisemeMap.Add( "AA", "Ao" );
            phonemeToVisemeMap.Add( "AAN", "Ao" );
            phonemeToVisemeMap.Add( "AO", "Ao" );
            phonemeToVisemeMap.Add( "AON", "Ao" );
            phonemeToVisemeMap.Add( "O",  "Ao" );
            phonemeToVisemeMap.Add( "ON", "Ih" );
            phonemeToVisemeMap.Add( "UW", "oh" );
            phonemeToVisemeMap.Add( "UY", "OO" );
            phonemeToVisemeMap.Add( "EU", "OO" );
            phonemeToVisemeMap.Add( "OE", "oh" );
            phonemeToVisemeMap.Add( "OEN", "oh" );
            phonemeToVisemeMap.Add( "AH", "Ih" );
            phonemeToVisemeMap.Add( "IH", "Ih" );
            phonemeToVisemeMap.Add( "UU", "oh" );
            phonemeToVisemeMap.Add( "UH", "oh" );
            phonemeToVisemeMap.Add( "AX", "Ih" );
            phonemeToVisemeMap.Add( "UX", "Ih" );
            phonemeToVisemeMap.Add( "AE", "Ih" );
            phonemeToVisemeMap.Add( "ER", "Er" );
            phonemeToVisemeMap.Add( "AXR", "Er" );
            phonemeToVisemeMap.Add( "EXR", "Er" );

            phonemeToVisemeMap.Add( "EY", "Ih" );
            phonemeToVisemeMap.Add( "AW", "Ih" );
            phonemeToVisemeMap.Add( "AY", "Ih" );
            phonemeToVisemeMap.Add( "OY", "oh" );
            phonemeToVisemeMap.Add( "OW", "oh" );

            phonemeToVisemeMap.Add( "SIL", "_" );
            }
            else if (mapping == "sbm2")
            {
                // taken from an FaceFX File->Export XML Actor from example_sbm2_mapping.facefx

                phonemeToVisemeMap.Add( "P", "BMP" );
                phonemeToVisemeMap.Add( "B", "BMP" );
                phonemeToVisemeMap.Add( "T", "D" );
                phonemeToVisemeMap.Add( "D", "D" );
                phonemeToVisemeMap.Add( "M", "BMP" );
                phonemeToVisemeMap.Add( "RA", "L" );
                phonemeToVisemeMap.Add( "RU", "Er" );
                phonemeToVisemeMap.Add( "FLAP", "D" );
                phonemeToVisemeMap.Add( "PH", "F" );
                phonemeToVisemeMap.Add( "F", "F" );
                phonemeToVisemeMap.Add( "V", "F" );
                phonemeToVisemeMap.Add( "TH", "Th" );
                phonemeToVisemeMap.Add( "DH", "Th" );
                phonemeToVisemeMap.Add( "S", "Z" );
                phonemeToVisemeMap.Add( "Z", "Z" );
                phonemeToVisemeMap.Add( "R", "R" );
                phonemeToVisemeMap.Add( "L", "L" );
                phonemeToVisemeMap.Add( "E", "Eh" );
                phonemeToVisemeMap.Add( "EN", "Eh" );
                phonemeToVisemeMap.Add( "EH", "Eh" );
                phonemeToVisemeMap.Add( "A", "Aa" );
                phonemeToVisemeMap.Add( "IH", "Ih" );
                phonemeToVisemeMap.Add( "ER", "Er" );
                phonemeToVisemeMap.Add( "AXR", "Er" );
                phonemeToVisemeMap.Add( "EXR", "Er" );
                phonemeToVisemeMap.Add( "AY", "Ay" );
                phonemeToVisemeMap.Add( "ON", "Ow" );
                phonemeToVisemeMap.Add( "AX", "Ah" );
                phonemeToVisemeMap.Add( "UX", "Ah" );
                phonemeToVisemeMap.Add( "AE", "Ah" );
                phonemeToVisemeMap.Add( "AA", "Aa" );
                phonemeToVisemeMap.Add( "AAN", "Aa" );
                phonemeToVisemeMap.Add( "AO", "Aa" );
                phonemeToVisemeMap.Add( "AON", "Aa" );
                phonemeToVisemeMap.Add( "O", "Ow" );
                phonemeToVisemeMap.Add( "EY", "Eh" );
                phonemeToVisemeMap.Add( "UW", "W" );
                phonemeToVisemeMap.Add( "OW", "Ow" );
                phonemeToVisemeMap.Add( "OY", "Oy" );
                phonemeToVisemeMap.Add( "H", "H" );
                phonemeToVisemeMap.Add( "SH", "Sh" );
                phonemeToVisemeMap.Add( "ZH", "Sh" );
                phonemeToVisemeMap.Add( "N", "D" );
                phonemeToVisemeMap.Add( "NG", "D" );
                phonemeToVisemeMap.Add( "Y", "Sh" );
                phonemeToVisemeMap.Add( "UY", "W" );
                phonemeToVisemeMap.Add( "EU", "W" );
                phonemeToVisemeMap.Add( "IY", "Ih" );
                phonemeToVisemeMap.Add( "K", "Kg" );
                phonemeToVisemeMap.Add( "G", "Kg" );
                phonemeToVisemeMap.Add( "GH", "Kg" );
                phonemeToVisemeMap.Add( "JH", "Sh" );
                phonemeToVisemeMap.Add( "CH", "Sh" );
                phonemeToVisemeMap.Add( "CX", "H" );
                phonemeToVisemeMap.Add( "X", "H" );
                phonemeToVisemeMap.Add( "HH", "H" );
                phonemeToVisemeMap.Add( "W", "W" );
                phonemeToVisemeMap.Add( "TS", "Z" );
                phonemeToVisemeMap.Add( "OE", "W" );
                phonemeToVisemeMap.Add( "OEN", "W" );
                phonemeToVisemeMap.Add( "UU", "W" );
                phonemeToVisemeMap.Add( "AH", "Ah" );
                phonemeToVisemeMap.Add( "UH", "W" );
                phonemeToVisemeMap.Add( "AW", "Aw" );
                
                phonemeToVisemeMap.Add( "SIL", "_" );
            }


         for ( int i = 0; i < d.phonemeData.Count; i++ )
         {
            d.phonemeData[ i ].visemeMatch = phonemeToVisemeMap[ d.phonemeData[ i ].phoneme ];
         }



         XmlWriterSettings xmlWriterSettings = new XmlWriterSettings();
         xmlWriterSettings.Indent = true;
         xmlWriterSettings.IndentChars = ("    ");
         XmlWriter xmlWriter = XmlWriter.Create( d.outputFile, xmlWriterSettings );


         xmlWriter.WriteStartElement( "bml" );

         xmlWriter.WriteStartElement( "speech" );
         xmlWriter.WriteAttributeString( "id",     "sp1" );
         xmlWriter.WriteAttributeString( "start",  "0.0" );
         xmlWriter.WriteAttributeString( "ready",  "0.1" );
         xmlWriter.WriteAttributeString( "stroke", "0.1" );
         xmlWriter.WriteAttributeString( "relax",  "0.2" );
         xmlWriter.WriteAttributeString( "end",    "0.2" );

         xmlWriter.WriteStartElement( "text" );

         int timeMarker = 0;
         for ( int i = 0; i < d.wordBreakData.Count; i++ )
         {
            xmlWriter.WriteStartElement( "sync" );
            xmlWriter.WriteAttributeString( "id", "T" + timeMarker.ToString() );
            xmlWriter.WriteAttributeString( "time", d.wordBreakData[ i ].start.ToString() );
            xmlWriter.WriteEndElement();
            timeMarker++;

            xmlWriter.WriteString( d.wordBreakData[ i ].word );
            xmlWriter.WriteWhitespace( xmlWriterSettings.NewLineChars );
            xmlWriter.WriteWhitespace( xmlWriterSettings.IndentChars );
            xmlWriter.WriteWhitespace( xmlWriterSettings.IndentChars );
            xmlWriter.WriteWhitespace( xmlWriterSettings.IndentChars );

            xmlWriter.WriteStartElement( "sync" );
            xmlWriter.WriteAttributeString( "id", "T" + timeMarker.ToString() );
            xmlWriter.WriteAttributeString( "time", d.wordBreakData[ i ].end.ToString() );
            xmlWriter.WriteEndElement();
            timeMarker++;

            xmlWriter.WriteWhitespace( xmlWriterSettings.NewLineChars );
            xmlWriter.WriteWhitespace( xmlWriterSettings.IndentChars );
            xmlWriter.WriteWhitespace( xmlWriterSettings.IndentChars );

            if ( i != d.wordBreakData.Count - 1 )
               xmlWriter.WriteWhitespace( xmlWriterSettings.IndentChars );
         }

         xmlWriter.WriteEndElement();  // text


         xmlWriter.WriteStartElement( "description" );
         xmlWriter.WriteAttributeString( "level", "1" );
         xmlWriter.WriteAttributeString( "type",  "audio/x-wav" );

         xmlWriter.WriteStartElement( "file" );
         xmlWriter.WriteAttributeString( "ref", d.name );
         xmlWriter.WriteEndElement();

         xmlWriter.WriteEndElement();  // description


         xmlWriter.WriteEndElement();  // speech



         for ( int i = 0; i < d.phonemeData.Count; i++ )
         {
            xmlWriter.WriteStartElement( "lips" );
            xmlWriter.WriteAttributeString( "viseme", d.phonemeData[ i ].visemeMatch );
            xmlWriter.WriteAttributeString( "articulation", "1.0" );
            xmlWriter.WriteAttributeString( "start", d.phonemeData[ i ].start.ToString() );
            xmlWriter.WriteAttributeString( "ready", d.phonemeData[ i ].start.ToString() );
            xmlWriter.WriteAttributeString( "relax", d.phonemeData[ i ].end.ToString() );
            xmlWriter.WriteAttributeString( "end",   d.phonemeData[ i ].end.ToString() );
            xmlWriter.WriteEndElement();
         }


         xmlWriter.WriteStartElement( "curves" );
         for ( int i = 0; i < d.facefxCurveDataXML.Count; i++ )
         {
            xmlWriter.WriteStartElement( "curve" );
            xmlWriter.WriteAttributeString( "name", d.facefxCurveDataXML[ i ].name );
            xmlWriter.WriteAttributeString( "num_keys", d.facefxCurveDataXML[ i ].numKeys.ToString() );
            xmlWriter.WriteAttributeString( "owner", d.facefxCurveDataXML[ i ].owner );
            xmlWriter.WriteString( d.facefxCurveDataXML[ i ].curveData );
            xmlWriter.WriteEndElement();
         }
         xmlWriter.WriteEndElement();


         xmlWriter.WriteEndElement();  // bml
         xmlWriter.WriteWhitespace( xmlWriterSettings.NewLineChars );

         xmlWriter.Close();
         }
      }


      static public void ReadXMLFromAnimationAttr( XmlReader xmlReader, TimingData timingData, bool remapAnalysisActors )
      {
         timingData.phonemeData = new List<PhonemeData>();
         timingData.wordBreakData = new List<WordBreakData>();
         timingData.curveData = new List<CurveData>();
         timingData.facefxCurveDataXML = new List<FaceFXCurveDataXML>();

         XmlReader animation = xmlReader.ReadSubtree();
         while ( animation.Read() )
         {
            if ( animation.NodeType == XmlNodeType.Element && 
                 animation.Name == "phonemes" )
            {
               XmlReader phonemes = animation.ReadSubtree();

               while ( phonemes.Read() )
               {
                  // phonene line looks like:
                  //    <phoneme phoneme="SIL" start="0.000000" end="1.200000" />

                  if ( phonemes.NodeType == XmlNodeType.Element &&
                       phonemes.Name == "phoneme" )
                  {
                     string phoneme = phonemes.GetAttribute( "phoneme" );
                     double start = XmlConvert.ToDouble( phonemes.GetAttribute( "start" ) );
                     double end = XmlConvert.ToDouble( phonemes.GetAttribute( "end" ) );

                     timingData.phonemeData.Add( new PhonemeData( phoneme, start, end ) );
                  }
               }
               phonemes.Close();
            }
            else if ( animation.NodeType == XmlNodeType.Element && 
                      animation.Name == "words" )
            {
               XmlReader words = animation.ReadSubtree();

               while ( words.Read() )
               {
                  // word line:
                  //    <word start="1.200000" end="1.380000">If</word>

                  if ( words.NodeType == XmlNodeType.Element &&
                       words.Name == "word" )
                  {
                     double start = XmlConvert.ToDouble( words.GetAttribute( "start" ) );
                     double end = XmlConvert.ToDouble( words.GetAttribute( "end" ) );
                     string word = words.ReadElementString();

                     timingData.wordBreakData.Add( new WordBreakData( word, start, end ) );
                  }
               }
               words.Close();
            }
            else if ( animation.NodeType == XmlNodeType.Element && 
                      animation.Name == "curves" )
            {
               // curve line:
               //   <curve name="Head Yaw" num_keys="3" owner="analysis">2.823998 0.000000 0.000000 0.000000 3.174005 -1.599560 0.000000 0.000000 3.959330 0.000000 0.000000 0.000000 </curve>

               // description - http://www.facefx.com/documentation/2010/W99

               XmlReader curves = animation.ReadSubtree();

               while ( curves.Read() )
               {
                  if ( curves.NodeType == XmlNodeType.Element &&
                       curves.Name == "curve" )
                  {
                     string name = curves.GetAttribute( "name" );
                     int numKeys = XmlConvert.ToInt32( curves.GetAttribute( "num_keys" ) );
                     string owner = curves.GetAttribute( "owner" );
                     string curveString = curves.ReadElementString();
                     string [] curveStringSplit = curveString.Trim().Split();

                     if ( numKeys > 0 && curveStringSplit.Length != ( numKeys * 4 ) )
                     {
                        Console.WriteLine( "Reading curve data, '{0}' expected num_keys({1}) elements, but received {2}", name, numKeys * 4, curveStringSplit.Length );
                     }


                     // HACK - TODO - The FaceFX maya exporter doesn't allow viseme poses to be named a single character.
                     //               So, the poses had to be named with 2 characters.
                     //               This is fixed up here.  Use this hack until the FaceFX exporter is fixed.
                     if (name == "DD")
                         name = "D";
                     else if (name == "FF")
                         name = "F";
                     else if (name == "HH")
                         name = "H";
                     else if (name == "JJ")
                         name = "j";
                     else if (name == "LL")
                         name = "L";
                     else if (name == "RR")
                         name = "R";
                     else if (name == "WW")
                         name = "W";
                     else if (name == "ZZ")
                        name = "Z";


                     // HACK - TODO - Remap curve names until we figure out how Analysis Actors work in FaceFX
                     // only do this if -remap is specified
                     if ( remapAnalysisActors )
                     {
                        // these Analysis Actors are in the default set
                        if ( name == "Blink" )
                           name = "au_45";
                        if ( name == "Eye Pitch" )
                           name = "Eye Pitch";
                        if ( name == "Eye Yaw" )
                           name = "Eye Yaw";
                        if ( name == "Eyebrow Raise" )
                           name = "au_1";
                        if ( name == "Head Pitch" )
                           name = "Head Pitch";
                        if ( name == "Head Roll" )
                           name = "Head Roll";
                        if ( name == "Head Yaw" )
                           name = "Head Yaw";
                        if ( name == "Squint" )
                           name = "au_7";
                     }


                     timingData.facefxCurveDataXML.Add( new FaceFXCurveDataXML( name, numKeys, owner, curveString ) );


                     // read the split string into the data struct.  Each curve is 4 values:
                     //    Time in seconds
                     //    Value
                     //    Slope In
                     //    Slope Out

                     for ( int i = 0; i < curveStringSplit.Length; i += 4 )
                     {
                        if ( i + 3 >= curveStringSplit.Length )
                           continue;

                        double time     = XmlConvert.ToDouble( curveStringSplit[ i ] );
                        double value    = XmlConvert.ToDouble( curveStringSplit[ i + 1 ] );
                        double slopeIn  = XmlConvert.ToDouble( curveStringSplit[ i + 2 ] );
                        double slopeOut = XmlConvert.ToDouble( curveStringSplit[ i + 3 ] );

                        // find the previous curve of the same name and set the end time to the current.
                        int index = timingData.curveData.FindLastIndex( delegate( CurveData c ) { if ( c.name == name ) return !c.endTimeSet; else return false; } );
                        if ( index != -1 )
                        {
                           timingData.curveData[ index ].endTime = time;
                           timingData.curveData[ index ].endTimeSet = true;
                        }

                        timingData.curveData.Add( new CurveData( name, time, value, slopeIn, slopeOut ) );
                     }
                  }
               }
               curves.Close();
            }
         }

         // make sure all endTime's have been set
         foreach ( CurveData c in timingData.curveData )
         {
            if ( !c.endTimeSet )
            {
               c.endTime = c.startTime;
               c.endTimeSet = true;
            }
         }

         // sort the curve data because by default, it's sorted by viseme
         timingData.curveData.Sort();

         /*
         foreach ( CurveData c in timingData.curveData )
         {
            Console.WriteLine( "{0} - {1} {2} {3}", c.name, c.startTime, c.endTime, c.value );
         }
         */
      }

   }
}
