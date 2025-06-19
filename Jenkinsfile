import hudson.model.Result

import static groovy.io.FileType.FILES  //isort: skip

properties(
      [
          parameters([
              [$class: 'ChoiceParameter',
                  choiceType: 'PT_SINGLE_SELECT',
                  description: 'Select a Browser',
                  name: 'BROWSER',
                  script: [$class: 'GroovyScript',
                      script: [
                          classpath: [],
                          sandbox: true,
                          script: """
                              return['chromium': 'chromium:selected', 'firefox': 'Firefox']
                          """.stripIndent()
                      ]
                  ]
              ],

              [$class: 'ChoiceParameter',
                  choiceType: 'PT_SINGLE_SELECT',
                  description: 'Select an ENV to run test.',
                  name: 'ENV',
                  script: [$class: 'GroovyScript',
                      script: [
                          classpath: [],
                          sandbox: true,
                          script: """
                              return['staging': 'STAGING:selected', 'dev': 'DEV', 'prod':'LIVE']
                          """.stripIndent()
                      ]
                  ]
              ],

              [$class: 'CascadeChoiceParameter',
                  choiceType: 'PT_SINGLE_SELECT',
                  description: 'Select a URL.',
                  name: 'TEST_URL',
                  referencedParameters: 'ENV',
                  script: [$class: 'GroovyScript',
                      script: [
                          classpath: [],
                          sandbox: true,
                          script: """
                              if (ENV == 'dev') {
                                  return[
                                          'https://automationexercise.com/':'DEV-1 [https://automationexercise.com/]'
                                      ]
                              }
                              else if(ENV == 'staging'){
                                  return ['https://automationexercise.com/:selected': 'STAGING [https://automationexercise.com/]']
                              }else if(ENV == 'prod'){
                                  return ['https://automationexercise.com/': 'LIVE [https://automationexercise.com/]']
                              }
                          """.stripIndent()
                      ]
                  ]
              ],

              choice(name: 'TESTTYPE', choices: ['SANITY', 'REGRESSION'], description: 'Select any of the testing types. REGRESSION_EXT stands for Extended Regression.'),

              [$class: 'CascadeChoiceParameter', choiceType: 'PT_SINGLE_SELECT', description: 'Select the threshold value for SANITY to trigger Regression and Ext Regression.',
              name: 'THRESHOLD',
              referencedParameters: 'TESTTYPE',
              script: [$class: 'GroovyScript',
              script: [
              classpath: [],
              sandbox: true,
              script: """
                if (TESTTYPE == 'SANITY') {
                  return [
                  '95': '95',
                  '80': '80',
                  '85': '85',
                  '90': '90'                  ]
                } else {
                  return [
                  '0': 'Not Applicable for Regression and EXT_Regression'
                  ]
                }
                """.stripIndent()
                ]
              ]
          ],

          [$class: 'CascadeChoiceParameter', choiceType: 'PT_SINGLE_SELECT', description: 'Select if you want to run regression test after the sanity test.',
              name: 'RUN_REGRESSION_AFTER_SANITY',
              referencedParameters: 'TESTTYPE',
              script: [$class: 'GroovyScript',
              script: [
              classpath: [],
              sandbox: true,
              script: """
                if (TESTTYPE == 'SANITY') {
                        return [
                            'false': 'No',
                            'true': 'Yes'

                        ]
                    } else {
                        return [
                            'false': 'Not Applicable for Regression and EXT_Regression'
                        ]
                    }
                """.stripIndent()
                ]
              ]
          ],


              [$class: 'CascadeChoiceParameter',
                choiceType: 'PT_CHECKBOX',
                description: 'There are some test cases which are marked as skipped for some reason. Select this option to execute skipped test cases.',
                name: 'EXECUTE_SKIPPED_TCS',
                referencedParameters: 'EXECUTE_FAILED_TCS',
                script: [$class: 'GroovyScript',
                script: [
                    classpath: [],
                    sandbox: true,
                    script: """
                        if(EXECUTE_FAILED_TCS){
                          return[
                               'yes': 'Execute Skipped TC(s):disabled'
                          ]
                        }else{
                          return[
                               'yes': 'Execute Skipped TC(s)'
                          ]
                        }
                        """.stripIndent()
                    ]
                ]
              ],

              [$class: 'CascadeChoiceParameter',
                choiceType: 'PT_CHECKBOX',
                description: 'Check this option if you want to execute all the test suites at one go.',
                name: 'SELECT_ALL',
                referencedParameters: 'EXECUTE_FAILED_TCS',
                script: [$class: 'GroovyScript',
                script: [
                    classpath: [],
                    sandbox: true,
                    script: """
                        if(EXECUTE_FAILED_TCS){
                          return[
                               'select_all': 'Select All:disabled'
                          ]
                        }else{
                          return[
                               'select_all': 'Select All'
                          ]
                        }
                        """.stripIndent()
                  ]
                ]
              ],


              [$class: 'CascadeChoiceParameter',
                choiceType: 'PT_CHECKBOX',
                description: 'List of all test suites. Select test suite(s) you need to execute.',
                name: 'TESTCASE',
                referencedParameters: 'SELECT_ALL, EXECUTE_FAILED_TCS',
                script: [$class: 'GroovyScript',
                fallbackScript: [
                    classpath: [],
                    sandbox: true,
                    script: 'return ["ERROR"]'
                ],
                script: [
                    classpath: [],
                    sandbox: true,
                    script: """
                        if(SELECT_ALL == 'select_all'){
                            return[
                               ${getSelectedTestsuiteList()}
                          ]
                        }else{
                            return[
                               ${getDeSelectedTestsuiteList()}
                          ]
                        }
                        """.stripIndent()
                ]
            ]
        ],
       ])
      ]
  )

  node {
      cleanWs()
      def repoInformation = checkout scm
      def GIT_COMMIT_HASH = repoInformation.GIT_COMMIT

      wrap([$class: 'BuildUser']) {
         jobUserId = "${BUILD_USER_ID}"
         jobUserName = "${BUILD_USER}"
      }

      currentBuild.displayName = "# ${currentBuild.number} run by ${jobUserId.toUpperCase()} on ${repoInformation.GIT_BRANCH.replace('origin/', '').toUpperCase()}"

      def _gchat_webhook_link = null
      def props = readProperties  file: 'resources/jenkins.properties'

      def providedENV = params.ENV
      def providedTestType = params.TESTTYPE
      def providedURL = params.TEST_URL

      try{
         if (jobUserId == 'timer' || jobUserId == 'remoteRequest'){
            _gchat_webhook_link = props["gchat_ci_cd_webhook_link"]
          }else{
            def dev_user_group = props["dev_user_group"]
            def staging_user_group = props["staging_user_group"]
            def live_user_group = props["live_user_group"]

            dev_users_list = dev_user_group.split(',')
            staging_users_list = staging_user_group.split(',')
            live_users_list = live_user_group.split(',')

            if(JOB_NAME == 'ScribePortalAutomation_RnD'){
               _gchat_webhook_link = props['gchat_rnd_webhook_link']
            }else if(dev_users_list.contains(jobUserId)){
              _gchat_webhook_link = props['gchat_dev_webhook_link']
            }else if(staging_users_list.contains(jobUserId)){
              _gchat_webhook_link = props['gchat_staging_webhook_link']
            }else if(live_users_list.contains(jobUserId)){
              _gchat_webhook_link = props['gchat_webhook_link']
            }
          }

      stage('G-chat Notfication [Starting Test]'){
          def startMessage = "*AutomationExercise* script execution is started with the following details.\nPlease keep an eye for its completion.\n-----------------------------------------------------------------------------------------------------*\n\n"
          def buildNumber = "*Build number:* " + currentBuild.number + "\n"
          def buildInitiatedBy = "*Build Initiated by:* ${jobUserId.toUpperCase()}\n\n"
          def gitBranch = "*GIT Branch:* ${repoInformation.GIT_BRANCH}\n\n"
          def testType = "*Test type:* ${providedTestType.toUpperCase()}\n"
          def testENV = "*Test ENV:* ${providedENV.toUpperCase()}\n"
          def testURL = "*Test URL:* ${providedURL}\n"
          def buildURL = "*Build URL:* ${JOB_URL}\n\n"

          def message = startMessage + buildNumber + buildInitiatedBy + gitBranch + testType + testENV + testURL + buildURL

          //googlechatnotification message: message, url: _gchat_webhook_link
      }

       def parallelTestConfiguration = [
            getParallelConfigurationData()
        ]

        def stepList = prepareBuildStages(parallelTestConfiguration)

        for (def groupOfSteps in stepList) {
          parallel groupOfSteps
        }

        currentBuild.result = "SUCCESS"
      } catch(error) {
        currentBuild.result = "FAILURE"
        echo "The following error occurred: ${error}"
        throw error
      } finally {

        npm i -g allure-commandline

        allure([
          includeProperties: false,
          jdk: '',
          properties: [],
          results: [[path: 'target/allure-results']]
        ])

        def gchat_webhook_link = props['gchat_webhook_link']
        String downstream_job_name = props['downstream_job_name']

        def summary = junit testResults: 'testResults/**/*.xml'
        int totalFailed = summary.failCount
        int totalSkipped = summary.skipCount
        int totalCount = summary.totalCount
        int totalExecuted = totalCount - totalSkipped
        double percentFailed = 0

        double percentPassed = 100 - (totalFailed * 100 / totalExecuted)
        int sanity_benchmark = Integer.parseInt(params.THRESHOLD ?: '95')

        if(percentPassed >= sanity_benchmark){
            currentBuild.rawBuild.@result = hudson.model.Result.SUCCESS
        }

        if(jobUserId == "timer"){
          jobUserId = "SCHEDULER"
        }

        def dev_user_list
        def staging_user_list
        def live_user_list

        stage("G-chat notifier"){
          def now = new Date()

          def summaryMsg = ""

          if(totalCount == 0){
            summaryMsg = "*Ooops!!!* there were no test cases to run. Possibly the user: *${jobUserId}* hasn't selected any of the test suites!\n\n"
          }else{
              percentFailed = totalFailed * 100 / totalExecuted
              if(totalFailed){
                summaryMsg = "${totalFailed} (${percentFailed.round(2)}%) failed out of ${totalExecuted} test cases.\n\n"
              }else{
                summaryMsg = "All passed (out of ${totalExecuted})!!!\n\n"
              }
          }

          def failedTestPropertiesFileInJenkins = "${JENKINS_HOME}/scp_failed_test_${params.TESTTYPE}.properties"
          def failedTestPropertiesFileInResourceFolder = "resources/scp_failed_test_${params.TESTTYPE}.properties"

          if(params.EXECUTE_FAILED_TCS){
              def failedTestProperties = readProperties  file: failedTestPropertiesFileInJenkins
              providedENV = failedTestProperties['env']
              providedURL = failedTestProperties['url']
              providedTestType = failedTestProperties['testtype']
          }

          def startMessage = "*AutomationExercise* script execution is completed. Please see the details (All calculations are EXCLUSIVE of Skipped TCs.):*\n*------------------------------------------------------------------------------------------------------------------------------------------*\n\n"
          def buildStatus = "*Build status:* " + currentBuild.result + "\n"
          def buildNumber = "*Build number:* " + currentBuild.number + "\n"
          def upstreamProjectName = "*Upstream Project Name:* " + env.UPSTREAM_PROJECT_NAME + "\n"
          def upstreamProjectBuildNo = "*Upstream Project Build number:* " + env.UPSTREAM_PROJECT_BUILD_NO + "\n"
          def buildStarted = "*Build started:* " + env.BUILD_TIMESTAMP + "\n"
          def buildEnded = "*Build ended:* " + now.format("YYYY-MM-dd HH:mm:ss", TimeZone.getTimeZone('BST')) + " BDT\n"
          def buildDuration = "*Duration:* " + currentBuild.durationString + "\n\n"
          def gitBranch = "*GIT Branch:* ${repoInformation.GIT_BRANCH}\n\n"
          def testType = "*Test type:* ${providedTestType.toUpperCase()}\n"
          def testENV = "*Test ENV:* ${providedENV.toUpperCase()}\n"
          def testURL = "*Test URL:* ${providedURL}\n"
          def buildURL = "*Build URL:* ${JOB_URL}\n"
          def reportLink = "*Report URL:* ${BUILD_URL}allure/\n\n"

          def message = ''
          if(env.UPSTREAM_PROJECT_BUILD_NO){
            message = startMessage + summaryMsg + buildStatus + buildNumber + buildInitiatedBy + upstreamProjectName + upstreamProjectBuildNo + buildStarted + buildEnded + buildDuration + gitBranch + testType + testENV + testURL + buildURL + reportLink
          }else{
            message = startMessage + summaryMsg + buildStatus + buildNumber + buildInitiatedBy + buildStarted + buildEnded + buildDuration + gitBranch + testType + testENV + testURL + buildURL + reportLink
          }

         //googlechatnotification message: message, url: _gchat_webhook_link
        }


        if((percentPassed >= sanity_benchmark && params.TESTTYPE == "SANITY"  &&  (jobUserId == "SCHEDULER" || jobUserId == "remoteRequest")) || (params.RUN_REGRESSION_AFTER_SANITY == true && params.SELECT_ALL == 'select_all')){
          stage("Regression Triggering"){
              print("Sanity successfully done. Triggering core regression...")
              build job: "${downstream_job_name}", parameters: [
                  string(name: "ENV", value: "${params.ENV}"),
                  string(name: "TEST_URL", value: "${params.TEST_URL}"),
                  string(name: "TESTTYPE", value: "REGRESSION"),
                  booleanParam(name: "EXECUTE_FAILED_TCS", value: false),
                  string(name: "THRESHOLD", value: "95"),
                  string(name: "USER", value: "${jobUserId}"),
                  string(name: "UPSTREAM_PROJECT_NAME", value: "${JOB_BASE_NAME}"),
                  string(name: "UPSTREAM_PROJECT_BUILD_NO", value: "${currentBuild.number}")
                ], propagate: false
          }
        }
      }
  }

  @NonCPS
  def getTestsuitePropertiesLoaded(){
    def currentDir = new File("${JENKINS_HOME}/workspace")
    def properties = new Properties()

    files_lst = []
    currentDir.traverse { File file ->
        if (file.name == 'testsuites.properties' && file.absolutePath.contains(JOB_NAME)) {
                def propertiesFile = new File(file.absolutePath)
                propertiesFile.withInputStream{
                    properties.load(it)
                }
        }
    }


    return properties.sort { it.value.toString().toLowerCase()}
  }

  def getFormattedTestsuiteName(String suiteName){
    def testType = ['Sanity', 'Regression']

    def splitted_testsuite_name = suiteName.split(':')
    int index = 0
    testsuite_name_decorated = splitted_testsuite_name[0] + " (" + splitted_testsuite_name.tail().collect({testType[index++] + ": " + it + " min(s)" }).join(' |§| ') + " )"
    return testsuite_name_decorated
  }

  def getEnabledTestsuiteList(){
    def properties = getTestsuitePropertiesLoaded()
    def suite_lst = []
    properties.each {
        def testsuite_name_decorated = getFormattedTestsuiteName(it.value)
        suite_lst.add("'${it.key}': '${testsuite_name_decorated}'")
    }
    return suite_lst
  }

  def getDisabledTestsuiteList(){
    def properties = getTestsuitePropertiesLoaded()
    def suite_lst = []
    properties.each {
        def testsuite_name_decorated = getFormattedTestsuiteName(it.value)
        suite_lst.add("'${it.key}': '${testsuite_name_decorated}:disabled'")
    }
    return suite_lst.join(',')
  }

  def getSelectedTestsuiteList(){
    def properties = getTestsuitePropertiesLoaded()
    def suite_lst = []
    properties.each {
        def testsuite_name_decorated = getFormattedTestsuiteName(it.value)
        suite_lst.add("'${it.key}': '${testsuite_name_decorated}:selected'")
    }
    return suite_lst.join(',')
  }

  def getDeSelectedTestsuiteList(){
    def properties = getTestsuitePropertiesLoaded()
    def suite_lst = []
    properties.each {
        def testsuite_name_decorated = getFormattedTestsuiteName(it.value)
        suite_lst.add("'${it.key}': '${testsuite_name_decorated}'")
    }
    return suite_lst.join(',')
  }

  def getPytestCollectedItems(String fileName){
      def pytest_collected_items = sh (
        script: "set +x; virtualenv venv; . venv/bin/activate;pip3 install -r requirements.txt;python3 -m pytest --browser chromium ${fileName} --collect-only | grep -Eo 'collected [0-9]+ items?|[0-9]+ deselected|[0-9]+ selected'; set -x",
        returnStdout: true
       ).trim()

       return pytest_collected_items
  }

  def getParallelConfigurationData(){
    def properties = getTestsuitePropertiesLoaded()

    def testsuite_map = [:]
    properties.each {
        testsuite_map.put(it.value.split(":")[0], it.key)
    }

    return testsuite_map
  }


  def prepareBuildStages(List<Map<String,String>> parallelTestConfiguration) {
    def stepList = []

    println('Preparing builds...')

    for (def parallelConfig in  parallelTestConfiguration) {
      def parallelSteps = prepareParallelSteps(parallelConfig)
      stepList.add(parallelSteps)
    }

    println('Finished preparing builds!')

    return stepList
  }


  def prepareParallelSteps(Map<String, String> parallelStepsConfig) {
    def testcases = params.TESTCASE
    String [] testcaseList = testcase.split(',')
    def parallelSteps = [:]

    wrap([$class: 'BuildUser']) {
        jobUserId = "${BUILD_USER_ID}"
    }

  if(jobUserId == "remoteRequest" || jobUserId == "SCHEDULER"){
      parallelStepsConfig.each{
        def key = it.key
        def value = it.value
        def tmp = value.split('/')
        def suiteName = tmp[tmp.size() - 1]
        def pytest_count_list = getPytestCollectedItems(value).split("\n")
        if(pytest_count_list.contains('0 selected')){
            println("No *${params.TESTTYPE.toLowerCase()}* test cases found in ${value}")
        }else{
            parallelSteps.put(suiteName, prepareOneBuildStage(suiteName, value))
        }
      }
  }else{
      def execute_failed_tcs = params.EXECUTE_FAILED_TCS
      if(execute_failed_tcs){
        def failed_tests_props = readProperties file: failedTestPropertiesFileInJenkins
        def failed_test_list = failed_tests_props['failed_tcs']

        def testCaseList = failed_test_list.split(' ')

        for(def key in testCaseList){
          def tmp = key.replace('.py', '').split('/')
          def suiteName = tmp[tmp.size() - 1].split('_').join(' ')
          parallelSteps.put(suiteName, prepareOneBuildStage(suiteName, key))
        }
      }else{
        for(def key in testcaseList){
          def tmp = key.split('/')
          def suiteName = tmp[tmp.size() - 1]
          def pytest_count_list = getPytestCollectedItems(key).split("\n")

          if(pytest_count_list.contains('0 selected')){
              println("No *${params.TESTTYPE.toLowerCase()}* test cases found in ${key}")
          }else{
            parallelSteps.put(suiteName, prepareOneBuildStage(suiteName, key))
          }
        }
      }
    }

    return parallelSteps
  }


  def prepareOneBuildStage(String name, String file) {
    return {
      stage("Test: ${name}") {
            def EXECUTE_SKIPPED = params.EXECUTE_SKIPPED_TCS
            if(params.EXECUTE_SKIPPED_TCS != 'yes'){
              EXECUTE_SKIPPED = 'no'
            }

            if(jobUserId == 'timer'){
              sh """
                set +x
                rm -rf ${WORKSPACE}/allure-results ${WORKSPACE}/testResults/ && python3 -m pytest --browser ${params.BROWSER.toLowerCase()} --env=staging ${file} --run-skipped=${EXECUTE_SKIPPED} --junitxml=${WORKSPACE}/testResults/${file}.xml --alluredir=${WORKSPACE}/allure-results -rA
                set -x
                """
            }else{
              if(params.TEST_URL == ''){
                sh """
                set +x
                virtualenv venv
             . venv/bin/activate
             pip3 install -r requirements.txt
                rm -rf ${WORKSPACE}/allure-results ${WORKSPACE}/testResults/ && python3 -m pytest  --browser ${params.BROWSER.toLowerCase()} --env=${params.ENV.toLowerCase()} ${file} --run-skipped=${EXECUTE_SKIPPED} --junitxml=${WORKSPACE}/testResults/${file}.xml --alluredir=${WORKSPACE}/allure-results -rA
                set -x
                """
              }else{
                sh """
                set +x
                virtualenv venv
             . venv/bin/activate
             pip3 install -r requirements.txt
                rm -rf ${WORKSPACE}/allure-results ${WORKSPACE}/testResults/ && python3 -m pytest --browser ${params.BROWSER.toLowerCase()} --env=${params.ENV.toLowerCase()} --url=${params.TEST_URL} ${file} --run-skipped=${EXECUTE_SKIPPED} --junitxml=${WORKSPACE}/testResults/${file}.xml --alluredir=${WORKSPACE}/allure-results -rA
                set -x
                """
              }
            }
      }
    }
  }
