//This file creates outlines a session object that stores global variables while the user is interacting with the website.

class SessionManager {
    constructor() {
        this._userName = '';
        this._projectTitle = '';
        this._highlightedQuestionId = null;
        this._qaList = [];

        this.mainLLMInstructions =
`- If the context provided is insufficient for a detailed response, state 'I don't know.'
- Ignore the dates as the context might be outdated.
- Answer the question directly without unnecessary information.
- Do not reference previously answered questions or attached documents.
- Write in smooth, connected sentences.
- Focus solely on the question, using only necessary parts of the context.
- Present answers in an easily readable, human-like manner.
- Provide short and concise answers without explaining abbreviations.
- Break down the question and answer in multiple steps, addressing each subquestion. If unknown, state 'I don't know.'
`;
    }

    // Getters and Setters for userName
    get userName() {
        return this._userName;
    }

    set userName(name) {
        this._userName = name;
    }

    // Getters and Setters for projectTitle
    get projectTitle() {
        return this._projectTitle;
    }

    set projectTitle(title) {
        this._projectTitle = title;
    }

    // Getters and Setters for highlightedQuestionId
    get highlightedQuestionId() {
        return this._highlightedQuestionId;
    }

    set highlightedQuestionId(id) {
        this._highlightedQuestionId = id;
    }


    get qaList(){
        return this._qaList;
    }

    set qaList(qaList){
        this._qaList = qaList;
    }

    get mainLLMInstructions(){
        return this._mainLLMInstructions;
    }

    set mainLLMInstructions(instructions){
        this._mainLLMInstructions = instructions;
    }
    

}

export const session = new SessionManager();
