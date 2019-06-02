class IncorrectTreeError(Exception):
    """
    Used for error outputs occuring during tree creation or when accessing an object of class Node or DependencyTree
    (note that objects of class DependencyAnalysis or SentenceAnalysisConnector may access objects of class Node or
    DependencyTree)
    """
    def __init__(self, error_code):
        if error_code == 1:
            self.message = "Ungültige Anzahl Kanten"
        elif error_code == 2:
            self.message = "Ungültige Anzahl Wurzel(n)"
        elif error_code == 3:
            self.message = "Zyklus oder Knoten mit mehreren Eltern"
        elif error_code == 4:
            self.message = "Ungültige Wurzel"
        elif error_code == 10:
            self.message = "Kein Baum vorhanden"
        elif error_code == 100:
            self.message = "Kein Knoten eingegeben"
        elif error_code == 101:
            self.message = "Ungültiges Label eingegeben"
        else:
            self.message = "Unspezifischer Baumfehler"

    def __str__(self):
        return self.message


class IncorrectInstantiationError(Exception):
    """
    Used for error outputs occurring during creation of general SentenceObject
    """
    def __init__(self, error_code):
        if error_code == 0:
            self.message = "Keine Satz-ID angegeben"
        elif error_code == 1:
            self.message = "Ungültige Satz-ID angegeben"
        elif error_code == 2:
            self.message = "Keine Tokens eingegeben"
        elif error_code == 3:
            self.message = "Kein Baum eingegeben"
        elif error_code == 4:
            self.message = "Unvollständige Kante eingegeben"
        elif error_code == 5:
            self.message = "Keine korrekte Analyse angegeben"
        elif error_code == 6:
            self.message = "Keine gültige Lemmata-Liste angegeben"
        elif error_code == -1:
            self.message = "Ungültige Eingabe"
        else:
            self.message = "unspezifischer Fehler bei der Erstellung"

    def __str__(self):
        return self.message


class ConnectorError (Exception):
    """
    Used for errors during access of specific DependencyAnalysis
    """

    def __init__(self, error_code):
        if error_code == 1:
            self.message = "Kein Dependenzbaum vorhanden"
        if error_code == 2:
            self.message = "Keine valide Analyse vorhanden"
        else:
            self.message = "Unspezifischer Analysefehler"

    def __str__(self):
        return self.message


class KMeanError (Exception):
    """
    Used for errors resulting of actions by class KMeanHelper
    note that this includes an error if no valid k-mean result could be calculated (i.e. not even two results were the
    same)
    """

    def __init__(self, error_code):
        if error_code == 0:
            self.message = "bei K-Means-Durchführung"
        elif error_code == 1:
            self.message = "Values < 0 eingegeben"
        elif error_code == 2:
            self.message = "Values > 0 und < 1 "
        elif error_code == -1:
            self.message = "Zu wenig Objekte für eingegebene Anzahl Cluster"
        elif error_code == -2:
            self.message = "Zu wenig potentielle Cluster für eingegebene Objekte"
        elif error_code == -3:
            self.message = "Mindestens ein doppelter Key angegeben"
        elif error_code == 3:
            self.message = "Kein schlüssiges K-Mean-Ergebnis"
        elif error_code == 4:
            self.message = "Keine gültige Angabe für maximale K-Mean Versuche"
        elif error_code == 6:
            self.message = "Zu wenig Versuche für K-Mean-Ergebnis-Vergleich angegeben"
        elif error_code == 7:
            self.message = "Fehler bei Neuberechnung der Cluster-Zentren"
        else:
            self.message = "Unspezifischer Fehler bei K-Means"

    def __str__(self):
        return self.message


class ValencyFrameError (Exception):
    """
    Used for errors occurring during access of object of class ValencyFrame
    """

    def __init__(self, error_code):
        if error_code == 1:
            self.message = "Fehler beim Kopieren"
        elif error_code == 2:
            self.message = "Ungültige Analyse"
        elif error_code == 3:
            self.message = "Fehler beim Aufruf von S-ID in S-ID- to W-ID- to Word-Mapping"
        elif error_code == 4:
            self.message = "Fehler beim Aufruf von W-ID in S-ID- to W-ID- to Word-Mapping"
        elif error_code == 5:
            self.message = "Fehler beim Setzen des Valenzrahmens, kein gültiges Dictionary angegeben"
        elif error_code == 7:
            self.message = "Fehler beim Setzen des aktuellen Komplement-Pattern-Dictionaries: leere Signatur angegeben"
        elif error_code == 8:
            self.message = "Fehler beim Setzen des aktuellen Komplement-Pattern-Dictionaries: Signatur ist kein Tupel"
        else:
            self.message = "Fehler bei Valenzrahmen"

    def __str__(self):
        return self.message


class ValencyAnalysisError (Exception):
    """
    Used for errors occurring during access of class ValencyAnalysis
    """

    def __init__(self, error_code):
        if error_code == 1:
            self.message = "Keine Analyse vorhanden"
        elif error_code == 2:
            self.message = "Falscher Parameter für K-Mean-Aufruf: Zu viele Cluster werden werden entfernt"
        elif error_code == 3:
            self.message = "Falscher Parameter für K-Mean-Aufruf: Nicht genügend Cluster für angegebene Auswahl"
        elif error_code == 4:
            self.message = "Keine Cluster für K-Mean-Aufruf angegeben"
        elif error_code == 5:
            self.message = "Falsche Häufigkeit für Beschneidung des Valenzrahmens angegeben"
        elif error_code == 6:
            self.message = "Keine Sätze im Valenzrahmen gefunden, Division durch Null"
        elif error_code == 7:
            self.message = "Falsche Eingabe zum Löschen von Signatur mittels Komplement-Klassen:" \
                           " keine gültige Komplement-Klasse angegeben"
        else:
            self.message = "Fehler in der Valenzanalyse"

    def __str__(self):
        return self.message
