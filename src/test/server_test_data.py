
# For server testing purposes - aka tests data
def get_test_payloads():
    return [
      Payload("suggestion_1_on:reviews-v1-7584579fb7-tckvz", {
        "type": "block_actions",
        "team": {
            "id": "TU739HPJL",
            "domain": "progmaticlabllc"
        },
        "user": {
            "id": "UU99F74MU",
            "username": "amorlang",
            "name": "amorlang",
            "team_id": "TU739HPJL"
        },
        "api_app_id": "AU73B5P24",
        "token": "mkv81FOLRwY7U0LML34egSEx",
        "container": {
            "type": "message",
            "message_ts": "1584018085.005300",
            "channel_id": "CUW6VHA80",
            "is_ephemeral": False
        },
        "trigger_id": "998205957078.959111601632.0f549e3db9c5c05c7bbfdcf61055324c",
        "channel": {
            "id": "CUW6VHA80",
            "name": "skynet-dbg"
        },
        "message": {
            "bot_id": "BU6L5GGSG",
            "type": "message",
            "text": "This+content+cant+be+displayed.",
            "user": "UU743B1K2",
            "ts": "1584018085.005300",
            "team": "TU739HPJL",
            "blocks": [
            {
                "type": "section",
                "block_id": "nJyJ",
                "text": {
                "type": "mrkdwn",
                "text": ":arrow_up:+Incident+3390305+is+created+with+the+following+anomaly+in+your+infrastructure+\nIt+could+be+solved+by+replacing+the+problematic+pod+reviews-v1-7584579fb7-tckvz",
                "verbatim": False
                }
            },
            {
                "type": "actions",
                "block_id": "actions1",
                "elements": [
                {
                    "type": "button",
                    "action_id": "x1Re",
                    "text": {
                    "type": "plain_text",
                    "text": "Use+Suggested+RunBook",
                    "emoji": True
                    },
                    "style": "primary",
                    "value": "suggestion_1_on:reviews-v1-7584579fb7-tckvz"
                },
                {
                    "type": "button",
                    "action_id": "tXlDr",
                    "text": {
                    "type": "plain_text",
                    "text": "Describe+Suggested+RunBook",
                    "emoji": True
                    },
                    "style": "primary",
                    "value": "suggestion_1_explain:reviews-v1-7584579fb7-tckvz"
                },
                {
                    "type": "button",
                    "action_id": "8DW",
                    "text": {
                    "type": "plain_text",
                    "text": "I+will+fix+myself",
                    "emoji": True
                    },
                    "style": "danger",
                    "value": "operator_flow:reviews-v1-7584579fb7-tckvz"
                },
                {
                    "type": "button",
                    "action_id": "ITw8",
                    "text": {
                    "type": "plain_text",
                    "text": "This+is+not+an+anomaly",
                    "emoji": True
                    },
                    "style": "primary",
                    "value": "negative_case:reviews-v1-7584579fb7-tckvz"
                }
                ]
            }
            ]
        },
        "response_url": "https://hooks.slack.com/actions/TU739HPJL/983208045010/BpAkwM424EejeJz7tPOMM7sG",
        "actions": [
            {
            "action_id": "tXlDr",
            "block_id": "actions1",
            "text": {
                "type": "plain_text",
                "text": "Describe+Suggested+RunBook",
                "emoji": True
            },
            "value": "suggestion_1_explain:reviews-v1-7584579fb7-tckvz",
            "style": "primary",
            "type": "button",
            "action_ts": "1584018162.274342"
            }
        ]
      }), 
      Payload("suggestion_1_on:reviews-v1-86d84b84bf-qbb7q", {
        "type": "block_actions",
        "team": {
          "id": "TU739HPJL",
          "domain": "progmaticlabllc"
        },
        "user": {
          "id": "UU99F74MU",
          "username": "amorlang",
          "name": "amorlang",
          "team_id": "TU739HPJL"
        },
        "api_app_id": "AU73B5P24",
        "token": "mkv81FOLRwY7U0LML34egSEx",
        "container": {
          "type": "message",
          "message_ts": "1584098101.000700",
          "channel_id": "CUW6VHA80",
          "is_ephemeral": False
        },
        "trigger_id": "998356845024.959111601632.14ceb5d2c40ecd189241d425c47669bd",
        "channel": {
          "id": "CUW6VHA80",
          "name": "skynet-dbg"
        },
        "message": {
          "bot_id": "BU6L5GGSG",
          "type": "message",
          "text": "This+content+cant+be+displayed.",
          "user": "UU743B1K2",
          "ts": "1584098101.000700",
          "team": "TU739HPJL",
          "blocks": [
            {
              "type": "section",
              "block_id": "MrM",
              "text": {
                "type": "mrkdwn",
                "text": ":arrow_up:+Incident+1930977+is+created+with+the+following+anomaly+in+your+infrastructure+\nIt+could+be+solved+by+replacing+the+problematic+pod",
                "verbatim": False
              }
            },
            {
              "type": "divider",
              "block_id": "PCAt"
            },
            {
              "type": "section",
              "block_id": "lflC",
              "text": {
                "type": "mrkdwn",
                "text": "*Replace+problematic+pod*",
                "verbatim": False
              },
              "accessory": {
                "type": "static_select",
                "placeholder": {
                  "type": "plain_text",
                  "text": "Select+pod",
                  "emoji": True
                },
                "options": [
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "productpage-v1-7ff7bc5579-w45mc",
                      "emoji": True
                    },
                    "value": "suggestion_1_on:productpage-v1-7ff7bc5579-w45mc"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "productpage-v1-7ff7bc5579-w45mc",
                      "emoji": True
                    },
                    "value": "suggestion_1_on:productpage-v1-7ff7bc5579-w45mc"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "productpage-v1-7ff7bc5579-w45mc",
                      "emoji": True
                    },
                    "value": "suggestion_1_on:productpage-v1-7ff7bc5579-w45mc"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "reviews-v1-86d84b84bf-qbb7q",
                      "emoji": True
                    },
                    "value": "suggestion_1_on:reviews-v1-86d84b84bf-qbb7q"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "reviews-v2-8665b7dd65-rvrwh",
                      "emoji": True
                    },
                    "value": "suggestion_1_on:reviews-v2-8665b7dd65-rvrwh"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "reviews-v3-9f9fc7b45-w2cmb",
                      "emoji": True
                    },
                    "value": "suggestion_1_on:reviews-v3-9f9fc7b45-w2cmb"
                  }
                ],
                "confirm": {
                  "title": {
                    "type": "plain_text",
                    "text": "Replace+selacted+pod?",
                    "emoji": True
                  },
                  "text": {
                    "type": "mrkdwn",
                    "text": "The+selected+pod+will+be+replaced+with+new+one",
                    "verbatim": False
                  },
                  "confirm": {
                    "type": "plain_text",
                    "text": "Confirm",
                    "emoji": True
                  },
                  "deny": {
                    "type": "plain_text",
                    "text": "No",
                    "emoji": True
                  }
                },
                "action_id": "rNEr"
              }
            },
            {
              "type": "section",
              "block_id": "P9V",
              "text": {
                "type": "mrkdwn",
                "text": "This+is+not+anomaly+for+pod",
                "verbatim": False
              },
              "accessory": {
                "type": "static_select",
                "placeholder": {
                  "type": "plain_text",
                  "text": "Select+pod",
                  "emoji": True
                },
                "options": [
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "productpage-v1-7ff7bc5579-w45mc",
                      "emoji": True
                    },
                    "value": "negative_case:productpage-v1-7ff7bc5579-w45mc"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "productpage-v1-7ff7bc5579-w45mc",
                      "emoji": True
                    },
                    "value": "negative_case:productpage-v1-7ff7bc5579-w45mc"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "productpage-v1-7ff7bc5579-w45mc",
                      "emoji": True
                    },
                    "value": "negative_case:productpage-v1-7ff7bc5579-w45mc"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "reviews-v1-86d84b84bf-qbb7q",
                      "emoji": True
                    },
                    "value": "negative_case:reviews-v1-86d84b84bf-qbb7q"
                  }, {
                    "text": {
                      "type": "plain_text",
                      "text": "reviews-v2-8665b7dd65-rvrwh",
                      "emoji": True
                    },
                    "value": "negative_case:reviews-v2-8665b7dd65-rvrwh"
                  }, {
                    "text": {
                      "type": "plain_text",
                      "text": "reviews-v3-9f9fc7b45-w2cmb",
                      "emoji": True
                    },
                    "value": "negative_case:reviews-v3-9f9fc7b45-w2cmb"
                  }
                ],
                "confirm": {
                  "title": {
                    "type": "plain_text",
                    "text": "This+is+not+anomaly?",
                    "emoji": True
                  },
                  "text": {
                    "type": "mrkdwn",
                    "text": "The+anomaly+for+selected+pod+will+be+marked+as+normal",
                    "verbatim": False
                  },
                  "confirm": {
                    "type": "plain_text",
                    "text": "Confirm",
                    "emoji": True
                  },
                  "deny": {
                    "type": "plain_text",
                    "text": "No",
                    "emoji": True
                  }
                },
                "action_id": "IyTL4"
              }
            },
            {
              "type": "section",
              "block_id": "6ug",
              "text": {
                "type": "mrkdwn",
                "text": "`This+is+not+anomaly+for+pod`",
                "verbatim": False
              },
              "accessory": {
                "type": "static_select",
                "placeholder": {
                  "type": "plain_text",
                  "text": "Select+pod",
                  "emoji": True
                },
                "options": [
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "productpage-v1-7ff7bc5579-w45mc",
                      "emoji": True
                    },
                    "value": "operator_flow:productpage-v1-7ff7bc5579-w45mc"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "productpage-v1-7ff7bc5579-w45mc",
                      "emoji": True
                    },
                    "value": "operator_flow:productpage-v1-7ff7bc5579-w45mc"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "productpage-v1-7ff7bc5579-w45mc",
                      "emoji": True
                    },
                    "value": "operator_flow:productpage-v1-7ff7bc5579-w45mc"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "reviews-v1-86d84b84bf-qbb7q",
                      "emoji": True
                    },
                    "value": "operator_flow:reviews-v1-86d84b84bf-qbb7q"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "reviews-v2-8665b7dd65-rvrwh",
                      "emoji": True
                    },
                    "value": "operator_flow:reviews-v2-8665b7dd65-rvrwh"
                  },
                  {
                    "text": {
                      "type": "plain_text",
                      "text": "reviews-v3-9f9fc7b45-w2cmb",
                      "emoji": True
                    },
                    "value": "operator_flow:reviews-v3-9f9fc7b45-w2cmb"
                  }
                ],
                "confirm": {
                  "title": {
                    "type": "plain_text",
                    "text": "This+is+not+anomaly?",
                    "emoji": True
                  },
                  "text": {
                    "type": "mrkdwn",
                    "text": "The+anomaly+for+selected+pod+will+be+marked+as+normal",
                    "verbatim": False
                  },
                  "confirm": {
                    "type": "plain_text",
                    "text": "Confirm",
                    "emoji": True
                  },
                  "deny": {
                    "type": "plain_text",
                    "text": "No",
                    "emoji": True
                  }
                },
                "action_id": "vY6BD"
              }
            }
          ]
        },
        "response_url": "https://hooks.slack.com/actions/TU739HPJL/998356844880/5DNSbh4Ybz3c0aOlPgUFBJLL",
        "actions": [
          {
            "confirm": {
              "title": {
                "type": "plain_text",
                "text": "Replace+selacted+pod?",
                "emoji": True
              },
              "text": {
                "type": "mrkdwn",
                "text": "The+selected+pod+will+be+replaced+with+new+one",
                "verbatim": False
              },
              "confirm": {
                "type": "plain_text",
                "text": "Confirm",
                "emoji": True
              },
              "deny": {
                "type": "plain_text",
                "text": "No",
                "emoji": True
              }
            },
            "type": "static_select",
            "action_id": "rNEr",
            "block_id": "lflC",
            "selected_option": {
              "text": {
                "type": "plain_text",
                "text": "reviews-v1-86d84b84bf-qbb7q",
                "emoji": True
              },
              "value": "suggestion_1_on:reviews-v1-86d84b84bf-qbb7q"
            },
            "placeholder": {
              "type": "plain_text",
              "text": "Select+pod",
              "emoji": True
            },
            "action_ts": "1584098244.490971"
          }
        ]
      })
    ]
