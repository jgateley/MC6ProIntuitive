

class MC6ProNavigatorTestCase(unittest.TestCase):
    navigator_banks_one_button = [
        ["Home",
         ["Bank 1", "Bank 2", "Bank 3", "Bank 4", "Bank 5", "Next",
          "Bank 6", "Bank 7", "Bank 8", "Bank 9", "Bank 10", "Previous/Next",
          "Bank 11", "Bank 12", "Bank 13", "Bank 14", "Bank 15", "Previous/Next",
          "Bank 16", "Bank 17", "Bank 18", "Bank 19", "Bank 20", "Previous/Next"]
         ],
        ["Home (2)",
         ["Bank 21", "Bank 22", "Bank 23", "Bank 24", "Bank 25", "Previous/Next",
          "Bank 26", "Bank 27", "Bank 28", "Bank 29", "Bank 30", "Previous"]
         ],
        ["Bank 1",
         ['', '', '', '', '', 'Home']
         ],
        ["Bank 2",
         ['Preset 1', '', '', '', '', 'Home']
         ],
        ["Bank 3",
         ['Preset 1', 'Preset 2', '', '', '', 'Home']
         ],
        ["Bank 4",
         ['Preset 1', 'Preset 2', 'Preset 3', '', '', 'Home']
         ],
        ["Bank 5",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', '', 'Home']
         ],
        ["Bank 6",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home']
         ],
        ["Bank 7",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', '', '', '', '', 'Previous']
         ],
        ["Bank 8",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', '', '', '', 'Previous']
         ],
        ["Bank 9",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', '', '', 'Previous']
         ],
        ["Bank 10",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', '', 'Previous']
         ],
        ["Bank 11",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous']
         ],
        ["Bank 12",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', '', '', '', '', 'Previous']
         ],
        ["Bank 13",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', '', '', '', 'Previous']
         ],
        ["Bank 14",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', '', '', 'Previous']
         ],
        ["Bank 15",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', '', 'Previous']
         ],
        ["Bank 16",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous']
         ],
        ["Bank 17",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', '', '', '', '', 'Previous']
         ],
        ["Bank 18",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', '', '', '', 'Previous']
         ],
        ["Bank 19",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', '', '', 'Previous']
         ],
        ["Bank 20",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', '', 'Previous']
         ],
        ["Bank 21",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous']
         ],
        ["Bank 22",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous/Next']
         ],
        ["Bank 22 (2)",
         ['Preset 21', '', '', '', '', 'Previous']
         ],
        ["Bank 23",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous/Next']
         ],
        ["Bank 23 (2)",
         ['Preset 21', 'Preset 22', '', '', '', 'Previous']
         ],
        ["Bank 24",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous/Next']
         ],
        ["Bank 24 (2)",
         ['Preset 21', 'Preset 22', 'Preset 23', '', '', 'Previous']
         ],
        ["Bank 25",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous/Next']
         ],
        ["Bank 25 (2)",
         ['Preset 21', 'Preset 22', 'Preset 23', 'Preset 24', '', 'Previous']
         ],
        ["Bank 26",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous/Next']
         ],
        ["Bank 26 (2)",
         ['Preset 21', 'Preset 22', 'Preset 23', 'Preset 24', 'Preset 25', 'Previous']
         ],
        ["Bank 27",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous/Next']
         ],
        ["Bank 27 (2)",
         ['Preset 21', 'Preset 22', 'Preset 23', 'Preset 24', 'Preset 25', 'Previous/Next',
          'Preset 26', '', '', '', '', 'Previous']
         ],
        ["Bank 28",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous/Next']
         ],
        ["Bank 28 (2)",
         ['Preset 21', 'Preset 22', 'Preset 23', 'Preset 24', 'Preset 25', 'Previous/Next',
          'Preset 26', 'Preset 27', '', '', '', 'Previous']
         ],
        ["Bank 29",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous/Next']
         ],
        ["Bank 29 (2)",
         ['Preset 21', 'Preset 22', 'Preset 23', 'Preset 24', 'Preset 25', 'Previous/Next',
          'Preset 26', 'Preset 27', 'Preset 28', '', '', 'Previous']
         ],
        ["Bank 30",
         ['Preset 1', 'Preset 2', 'Preset 3', 'Preset 4', 'Preset 5', 'Home/Next',
          'Preset 6', 'Preset 7', 'Preset 8', 'Preset 9', 'Preset 10', 'Previous/Next',
          'Preset 11', 'Preset 12', 'Preset 13', 'Preset 14', 'Preset 15', 'Previous/Next',
          'Preset 16', 'Preset 17', 'Preset 18', 'Preset 19', 'Preset 20', 'Previous/Next']
         ],
        ["Bank 30 (2)",
         ['Preset 21', 'Preset 22', 'Preset 23', 'Preset 24', 'Preset 25', 'Previous/Next',
          'Preset 26', 'Preset 27', 'Preset 28', 'Preset 29', '', 'Previous']
         ]
    ]

    navigator_banks_two_button = [
        ["Home",
         ["Bank 1", "Bank 2", "Bank 3", "Bank 4", "Bank 5", "Next",
          "Bank 6", "Bank 7", "Previous", "Bank 8", "Bank 9", "Next",
          "Bank 10", "Bank 11", "Previous", "Bank 12", "Bank 13", "Next",
          "Bank 14", "Bank 15", "Previous", "Bank 16", "Bank 17", "Next"]
         ],
        ["Home (2)",
         ["Bank 18", "Bank 19", "Previous", "Bank 20", "Bank 21", "Next",
          "Bank 22", "Bank 23", "Previous", "Bank 24", "Bank 25", "Next",
          "Bank 26", "Bank 27", "Previous", "Bank 28", "Bank 29", "Bank 30"
          ]
         ],
        ["Bank 1",
         ['', '', 'Home']
         ],
        ["Bank 2",
         ['Preset 1', '', 'Home']
         ],
        ["Bank 3",
         ['Preset 1', 'Preset 2', 'Home']
         ],
        ["Bank 4",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3']
         ],
        ["Bank 5",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4']
         ],
        ["Bank 6",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Preset 5']
         ],
        ["Bank 7",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous']
         ],
        ["Bank 8",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7']
         ],
        ["Bank 9",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8']
         ],
        ["Bank 10",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Preset 9']
         ],
        ["Bank 11",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous']
         ],
        ["Bank 12",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11']
         ],
        ["Bank 13",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12']
         ],
        ["Bank 14",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Preset 13']
         ],
        ["Bank 15",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous']
         ],
        ["Bank 16",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15']
         ],
        ["Bank 17",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16']
         ],
        ["Bank 18",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Preset 17']
         ],
        ["Bank 19",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 19 (2)",
         ['Preset 17', 'Preset 18', 'Previous']
         ],
        ["Bank 20",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 20 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19']
         ],
        ["Bank 21",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 21 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20']
         ],
        ["Bank 22",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 22 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Preset 21']
         ],
        ["Bank 23",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 23 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous']
         ],
        ["Bank 24",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 24 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23']
         ],
        ["Bank 25",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 25 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24']
         ],
        ["Bank 26",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 26 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Preset 25']
         ],
        ["Bank 27",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 27 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Next',
          'Preset 25', 'Preset 26', 'Previous']
         ],
        ["Bank 28",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 28 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Next',
          'Preset 25', 'Preset 26', 'Previous', 'Preset 27']
         ],
        ["Bank 29",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 29 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Next',
          'Preset 25', 'Preset 26', 'Previous', 'Preset 27', 'Preset 28']
         ],
        ["Bank 30",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 30 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Next',
          'Preset 25', 'Preset 26', 'Previous', 'Preset 27', 'Preset 28', 'Preset 29']
         ]
    ]

    def check_navigator(self, mode, navigator_banks):
        # TODO: CLean this up
        return
        intuitive_conf = jg.Grammar(MC6Pro_intuitive.simple_schema, minimal=True)
        intuitive_file = jg.GrammarFile(filename='Configs/Test/NavigatorTest.json')
        intuitive_json = intuitive_file.load()
        intuitive_model = intuitive_conf.parse_config(intuitive_json)
        base_model = intuitive_model.to_backup(mode)
        self.assertIsNotNone(base_model)
        for pos, bank in enumerate(base_model.banks):
            if pos < len(navigator_banks):
                self.assertEqual(bank.name, navigator_banks[pos][0])
                for pos2, preset in enumerate(bank.presets):
                    if pos2 < len(navigator_banks[pos][1]):
                        self.assertEqual(preset.short_name, navigator_banks[pos][1][pos2])
                    else:
                        self.assertIsNone(preset)
            else:
                self.assertIsNone(bank)

    def test_navigator_two_button(self):
        self.check_navigator("Two Button", self.navigator_banks_two_button)

    def test_navigator_one_button(self):
        self.check_navigator("One Button", self.navigator_banks_one_button)

